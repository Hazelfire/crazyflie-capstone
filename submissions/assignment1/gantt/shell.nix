{ pkgs ? import <nixpkgs> {}}:
pkgs.mkShell {
  name = "plantuml";
  buildInputs = with pkgs; [ plantuml ];
}
