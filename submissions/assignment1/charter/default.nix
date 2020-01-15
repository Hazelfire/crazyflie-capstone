{ pkgs ? import <nixpkgs> {} }:
  pkgs.stdenv.mkDerivation {
    name="capstoneTechnical";
    src=./.;
    buildInputs = with pkgs; [texlive.combined.scheme-basic];
    buildPhase = ''
    pdflatex document.tex
    '';
    installPhase = ''
      mkdir -p $out
      cp document.pdf $out
    '';
  }
