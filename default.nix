with import <nixpkgs> { };

let pythonPackages = python38Packages;
in pkgs.mkShell rec {
  venvDir = "./.venv";
  buildInputs = [
    pythonPackages.python
    pythonPackages.venvShellHook
  ];
}
