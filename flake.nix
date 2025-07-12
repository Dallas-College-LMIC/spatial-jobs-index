{
  description = "Spatial Jobs Index - Monorepo for backend API and frontend webapp";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";

    # Python backend dependencies
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, uv2nix, pyproject-nix, pyproject-build-systems }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (nixpkgs) lib;

        # Python backend setup
        python = pkgs.python313;
        backendWorkspace = uv2nix.lib.workspace.loadWorkspace {
          workspaceRoot = ./backend;
        };
        backendOverlay = backendWorkspace.mkPyprojectOverlay {
          sourcePreference = "wheel";
        };
        pyprojectOverrides = final: prev: {
          pyghtcast = prev.pyghtcast.overrideAttrs (old: {
            nativeBuildInputs = (old.nativeBuildInputs or []) ++ [
              final.poetry-core
            ];
          });
        };

        pythonSet = (pkgs.callPackage pyproject-nix.build.packages {
          inherit python;
        }).overrideScope (lib.composeManyExtensions [
          pyproject-build-systems.overlays.default
          backendOverlay
          pyprojectOverrides
        ]);

        # Backend virtual environment for production
        backendVenv = (pythonSet.mkVirtualEnv "spatial-index-api-env"
          backendWorkspace.deps.default).overrideAttrs
          (old: { venvIgnoreCollisions = [ "*" ]; });

        # Backend development virtual environment with all dependencies
        backendDevVenv = (pythonSet.mkVirtualEnv "spatial-index-api-dev-env"
          backendWorkspace.deps.all).overrideAttrs
          (old: { venvIgnoreCollisions = [ "*" ]; });

        # Docker image for backend
        backendDocker = pkgs.dockerTools.buildLayeredImage {
          name = "spatial-jobs-index-api";
          tag = "latest";
          contents = [ backendVenv pkgs.bash pkgs.coreutils ];
          config = {
            Cmd = [
              "${backendVenv}/bin/uvicorn"
              "app.main:app"
              "--host"
              "0.0.0.0"
              "--port"
              "8000"
            ];
            WorkingDir = "/app";
            ExposedPorts = { "8000/tcp" = { }; };
          };
        };

        # Frontend build using buildNpmPackage
        frontendBuild = pkgs.buildNpmPackage {
          pname = "sji-webapp";
          version = "0.1.0";
          src = ./frontend;

          # Use importNpmLock to avoid managing hashes
          npmDeps = pkgs.importNpmLock {
            npmRoot = ./frontend;
          };

          npmConfigHook = pkgs.importNpmLock.npmConfigHook;

          # Build the production bundle
          npmBuildScript = "build";

          installPhase = ''
            runHook preInstall
            mkdir -p $out
            cp -r dist/* $out/
            runHook postInstall
          '';
        };

        # Frontend development dependencies
        frontendNodeModules = pkgs.buildNpmPackage {
          pname = "sji-webapp-deps";
          version = "0.1.0";
          src = ./frontend;

          npmDeps = pkgs.importNpmLock {
            npmRoot = ./frontend;
          };

          npmConfigHook = pkgs.importNpmLock.npmConfigHook;
          dontNpmBuild = true;

          installPhase = ''
            runHook preInstall
            mkdir -p $out
            cp -r node_modules $out/
            runHook postInstall
          '';
        };

      in {
        packages = {
          # Backend packages
          backend = backendVenv;
          backend-docker = backendDocker;

          # Frontend packages
          frontend = frontendBuild;

          # Default package (you can change this to whatever makes sense)
          default = backendVenv;
        };

        apps = {
          # Backend app
          backend = {
            type = "app";
            program = "${pkgs.writeShellScriptBin "run-backend" ''
              cd ${./backend}
              ${backendVenv}/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
            ''}/bin/run-backend";
          };

          # Frontend dev server
          frontend = {
            type = "app";
            program = "${pkgs.writeShellScriptBin "run-frontend" ''
              # Create a temporary working directory
              WORK_DIR=$(mktemp -d)
              trap "rm -rf $WORK_DIR" EXIT

              echo "Setting up frontend development environment..."

              # Copy source files to working directory
              cp -r ${./frontend}/* $WORK_DIR/
              cp -r ${./frontend}/.[^.]* $WORK_DIR/ 2>/dev/null || true

              # Copy the pre-built node_modules (not symlink, to allow writes)
              echo "Copying dependencies..."
              cp -r ${frontendNodeModules}/node_modules $WORK_DIR/
              chmod -R u+w $WORK_DIR/node_modules

              # Change to working directory and run dev server
              cd $WORK_DIR
              echo "Starting frontend dev server on http://localhost:5173"
              exec ${pkgs.nodejs}/bin/npm run dev
            ''}/bin/run-frontend";
          };

          # Run both services
          default = {
            type = "app";
            program = "${pkgs.writeShellScriptBin "run-all" ''
              echo "Starting backend on port 8000..."
              cd ${./backend}
              ${backendVenv}/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
              BACKEND_PID=$!

              echo "Starting frontend on port 5173..."
              # Create a temporary writable directory for frontend
              WORK_DIR=$(mktemp -d)
              trap "rm -rf $WORK_DIR; kill $BACKEND_PID" EXIT

              # Copy frontend source to writable location
              cp -r ${./frontend}/* $WORK_DIR/
              cp -r ${./frontend}/.[^.]* $WORK_DIR/ 2>/dev/null || true

              # Copy the pre-built node_modules (not symlink, to allow writes)
              echo "Copying dependencies..."
              cp -r ${frontendNodeModules}/node_modules $WORK_DIR/
              chmod -R u+w $WORK_DIR/node_modules

              cd $WORK_DIR
              ${pkgs.nodejs}/bin/npm run dev &
              FRONTEND_PID=$!

              # Wait for Ctrl+C
              trap "kill $BACKEND_PID $FRONTEND_PID; rm -rf $WORK_DIR" INT
              wait
            ''}/bin/run-all";
          };
        };

        devShells = {
          # Backend development shell with pre-installed dependencies (uv2nix)
          backend = pkgs.mkShell {
            buildInputs = [
              backendDevVenv  # Virtual environment with all dependencies
              pkgs.ruff
              pkgs.uv
              pkgs.gcc
              pkgs.stdenv.cc.cc.lib
              pkgs.pre-commit
            ];

            env = {
              # Don't create venv using uv
              UV_NO_SYNC = "1";
              # Force uv to use Python interpreter from venv
              UV_PYTHON = "${backendDevVenv}/bin/python";
              # Prevent uv from downloading managed Python's
              UV_PYTHON_DOWNLOADS = "never";
            };

            shellHook = ''
              unset PYTHONPATH
              echo "Backend development shell activated (pure uv2nix)"
              echo "All Python dependencies are pre-installed via Nix"
              echo "Run 'cd backend' to enter the backend directory"
              echo "Run 'python -m uvicorn app.main:app --reload' to start the API"
              echo "Run 'pytest' to run tests (all dependencies available)"
            '';
          };

          # Backend development shell - impure (manual dependency management)
          backend-impure = pkgs.mkShell {
            buildInputs = [
              python
              pkgs.ruff
              pkgs.uv
              pkgs.gcc
              pkgs.stdenv.cc.cc.lib
              pkgs.pre-commit
            ] ++ (with pkgs.python313Packages; [
              mypy
              python-lsp-server
              python-lsp-ruff
              pylsp-mypy
            ]);

            env = {
              UV_PYTHON_DOWNLOADS = "never";
              UV_PYTHON = python.interpreter;
            };

            shellHook = ''
              unset PYTHONPATH
              echo "Backend development shell activated (impure)"
              echo "Run 'cd backend' to enter the backend directory"
              echo "Run 'uv sync' to install dependencies"
              echo "Run 'uv run python -m uvicorn app.main:app --reload' to start the API"
            '';
          };

          # Frontend development shell
          frontend = pkgs.mkShell {
            buildInputs = with pkgs; [
              nodejs
              nodePackages.npm
            ];

            shellHook = ''
              echo "Frontend development shell activated"
              echo "Run 'cd frontend' to enter the frontend directory"
              echo "Run 'npm install' to install dependencies"
              echo "Run 'npm run dev' to start the development server"
            '';
          };

          # Combined development shell
          default = pkgs.mkShell {
            buildInputs = [
              # Backend with pre-installed dependencies
              backendDevVenv
              # Backend tools
              pkgs.ruff
              pkgs.uv
              pkgs.gcc
              pkgs.stdenv.cc.cc.lib
              pkgs.pre-commit
              # Frontend tools
              pkgs.nodejs
              pkgs.nodePackages.npm
              # General tools
              pkgs.git
              pkgs.direnv
              # Database tools
              pkgs.postgresql
            ];

            env = {
              # Don't create venv using uv
              UV_NO_SYNC = "1";
              # Force uv to use Python interpreter from venv
              UV_PYTHON = "${backendDevVenv}/bin/python";
              # Prevent uv from downloading managed Python's
              UV_PYTHON_DOWNLOADS = "never";
            };

            shellHook = ''
              unset PYTHONPATH
              echo "Spatial Jobs Index Monorepo Development Shell"
              echo ""
              echo "Available commands:"
              echo "  nix run .#backend    - Run the backend API server"
              echo "  nix run .#frontend   - Run the frontend dev server"
              echo "  nix run              - Run both services"
              echo ""
              echo "  nix build .#backend        - Build backend package"
              echo "  nix build .#frontend       - Build frontend for production"
              echo "  nix build .#backend-docker - Build backend Docker image"
              echo ""
              echo "  nix develop .#backend  - Enter backend-only dev shell (with deps)"
              echo "  nix develop .#backend-impure - Enter backend shell (manual deps)"
              echo "  nix develop .#frontend - Enter frontend-only dev shell"
              echo ""
              echo "Backend Python dependencies are pre-installed via Nix"
            '';
          };
        };
      });
}
