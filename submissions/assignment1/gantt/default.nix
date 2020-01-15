{ pkgs ? import <nixpkgs> {} }:
pkgs.stdenv.mkDerivation {
  name="capstonegantt";
  buildInputs = with pkgs; [plantuml];
  src = ./.;
  buildPhase = ''
    plantuml gantt.plant
  '';
  installPhase = ''
    mkdir -p $out
    cp gantt.plant $out
  '';
}
