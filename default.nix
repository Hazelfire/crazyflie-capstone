{ nixpkgs ? import <nixpkgs> {  } }:

let

  pythonPackages = python-packages: with python-packages; [pip];
  
  cfdemos = nixpkgs.python.pkgs.callPackage ./cfdemos.nix {python=nixpkgs.python3;};

  pkgs = with nixpkgs; [
    neovim
    cfdemos
    libusb
    python37Packages.pyusb
    python37Packages.matplotlib
  ];

in
  nixpkgs.stdenv.mkDerivation {
    name = "env";
    propagatedBuildInputs = pkgs;
  }
