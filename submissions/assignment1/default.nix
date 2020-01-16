{ pkgs ? import <nixpkgs> {} }:
let
  charter = import ./charter {};
  technical = import ./technical {};
  gantt = import ./gantt {};
in
pkgs.stdenv.mkDerivation {
  name="capstoneassignment1";
  buildInputs = with pkgs; [zip];
  src = ./.;
  buildPhase = ''
    cp ${charter}/document.pdf Charter.pdf
    cp ${technical}/document.pdf TechnicalDesign.pdf
    cp ${gantt}/gantt.png Gantt.png
    zip -r submission.zip Charter.pdf TechnicalDesign.pdf Gantt.png AssessmentFormula.txt
  '';
  installPhase = ''
    mkdir -p $out
    cp submission.zip $out
  '';
}
