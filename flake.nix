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

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      uv2nix,
      pyproject-nix,
      pyproject-build-systems,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
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
            nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [
              final.poetry-core
            ];
          });
        };

        pythonSet =
          (pkgs.callPackage pyproject-nix.build.packages {
            inherit python;
          }).overrideScope
            (
              lib.composeManyExtensions [
                pyproject-build-systems.overlays.default
                backendOverlay
                pyprojectOverrides
              ]
            );

        # Backend virtual environment for production
        backendVenv =
          (pythonSet.mkVirtualEnv "spatial-index-api-env" backendWorkspace.deps.default).overrideAttrs
            (old: {
              venvIgnoreCollisions = [ "*" ];
            });

        # Backend development virtual environment with all dependencies
        backendDevVenv =
          (pythonSet.mkVirtualEnv "spatial-index-api-dev-env" backendWorkspace.deps.all).overrideAttrs
            (old: {
              venvIgnoreCollisions = [ "*" ];
            });

        # Docker image for backend
        backendDocker = pkgs.dockerTools.buildLayeredImage {
          name = "spatial-jobs-index-api";
          tag = "latest";
          contents = [
            backendVenv
            pkgs.bash
            pkgs.coreutils
          ];
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
            ExposedPorts = {
              "8000/tcp" = { };
            };
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

        # TDD Guard CLI tool
        tddGuard = pkgs.buildNpmPackage {
          pname = "tdd-guard";
          version = "0.8.1";

          src = pkgs.fetchFromGitHub {
            owner = "nizos";
            repo = "tdd-guard";
            rev = "v0.8.1";
            hash = "sha256-aPGtKCVfOd5J3C+iEPhTrLxNlEKs/FPn/5QNrkTX3T4=";
          };

          npmDepsHash = "sha256-Vw4pJXKUHGV3eMSaqZJ1kd+2edh89ch78W5p0bMhwqw=";

          # Fix broken symlinks
          postInstall = ''
            # Remove broken symlinks that cause build failure
            rm -f $out/lib/node_modules/tdd-guard/node_modules/tdd-guard-vitest
            rm -f $out/lib/node_modules/tdd-guard/node_modules/tdd-guard-jest
          '';
        };

        # Frontend build for local testing (with root base path)
        frontendBuildLocal = pkgs.buildNpmPackage {
          pname = "sji-webapp-local";
          version = "0.1.0";
          src = ./frontend;

          # Use importNpmLock to avoid managing hashes
          npmDeps = pkgs.importNpmLock {
            npmRoot = ./frontend;
          };

          npmConfigHook = pkgs.importNpmLock.npmConfigHook;

          # Override the build phase to build in development mode (which uses base: '/')
          buildPhase = ''
            runHook preBuild
            npm run type-check
            npx vite build --mode development
            runHook postBuild
          '';

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

      in
      {
        packages = {
          # Backend packages
          backend = backendVenv;
          backend-docker = backendDocker;

          # Frontend packages
          frontend = frontendBuild;
          frontend-local = frontendBuildLocal;

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
          # Combined development shell (impure approach for faster iteration)
          default = pkgs.mkShell {
            buildInputs = [
              # Use the Nix-managed Python virtual environment
              backendDevVenv
              # Frontend tools
              pkgs.nodejs
              pkgs.nodePackages.npm
              # General tools
              pkgs.just
              pkgs.ruff
              pkgs.gcc
              pkgs.stdenv.cc.cc.lib
              pkgs.pre-commit
              # Database tools
              pkgs.postgresql
              # TDD tools
              tddGuard
            ];

            shellHook = ''
              # The Nix-managed Python environment is automatically available
              echo "Spatial Jobs Index Monorepo Development Shell"
              echo ""
              echo "Python environment: Nix-managed (no uv sync needed)"
              echo "Python: $(which python)"
              echo ""
              echo "Backend commands:"
              echo "  pytest                    - Run backend tests"
              echo "  python -m uvicorn app.main:app --reload - Start API server"
              echo ""
              echo "Frontend setup:"
              echo "  cd frontend && npm install - Install frontend dependencies"
              echo "  npm run dev               - Start frontend dev server"
              echo ""
              echo "Available nix commands:"
              echo "  nix run .#backend    - Run the backend API server"
              echo "  nix run .#frontend   - Run the frontend dev server"
              echo "  nix run              - Run both services"
              echo ""
              echo "  nix build .#backend        - Build backend package"
              echo "  nix build .#frontend       - Build frontend for production"
              echo "  nix build .#backend-docker - Build backend Docker image"
            '';
          };
        };
      }
    );
}
