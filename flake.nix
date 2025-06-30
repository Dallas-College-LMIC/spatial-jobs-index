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
        pyprojectOverrides = _final: _prev: {};
        
        pythonSet = (pkgs.callPackage pyproject-nix.build.packages {
          inherit python;
        }).overrideScope (lib.composeManyExtensions [
          pyproject-build-systems.overlays.default
          backendOverlay
          pyprojectOverrides
        ]);
        
        # Backend virtual environment
        backendVenv = (pythonSet.mkVirtualEnv "spatial-index-api-env" 
          backendWorkspace.deps.default).overrideAttrs
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
        
        # Frontend build
        frontendBuild = pkgs.stdenv.mkDerivation {
          pname = "sji-webapp";
          version = "0.1.0";
          src = ./frontend;
          
          nativeBuildInputs = with pkgs; [ nodejs ];
          
          buildPhase = ''
            export HOME=$TMPDIR
            npm ci
            npm run build
          '';
          
          installPhase = ''
            mkdir -p $out
            cp -r dist/* $out/
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
              cd ${./frontend}
              ${pkgs.nodejs}/bin/npm run dev
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
              cd ${./frontend}
              ${pkgs.nodejs}/bin/npm run dev &
              FRONTEND_PID=$!
              
              # Wait for Ctrl+C
              trap "kill $BACKEND_PID $FRONTEND_PID" INT
              wait
            ''}/bin/run-all";
          };
        };
        
        devShells = {
          # Backend development shell
          backend = pkgs.mkShell {
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
              echo "Backend development shell activated"
              echo "Run 'cd backend' to enter the backend directory"
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
              # Backend tools
              python 
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
              echo "  nix develop .#backend  - Enter backend-only dev shell"
              echo "  nix develop .#frontend - Enter frontend-only dev shell"
            '';
          };
        };
      });
}