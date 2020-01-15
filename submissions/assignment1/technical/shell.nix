{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    name="capstoneCharter";
    buildInputs = with pkgs; [texlive.combined.scheme-full graphviz];
  }
