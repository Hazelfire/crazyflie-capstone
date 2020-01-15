{ pkgs ? import <nixpkgs> {} }:
let
  charter = import ./charter {};
  technical = import ./technical {};
  gantt = import ./gantt {};
in
pkgs.stdenv.mkDerivation {
  name="capstoneassignment1";
  buildInputs = with pkgs; [zip];
  unpackPhase = "true";
  buildPhase = ''
  zip -r submission.zip ${charter}/document.pdf ${technical}/document.pdf ${gantt}/gantt.png
  '';
  installPhase = ''
    mkdir -p $out
    cp submission.zip $out
  '';
}
