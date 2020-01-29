{ nixpkgs ? import <nixpkgs> {  } }:

let

  pythonPackages = python-packages: with python-packages; [pip];
  
  cflib = nixpkgs.callPackage ./cflib.nix {python=nixpkgs.python3;};

  pkgs = with nixpkgs; [
    neovim
    cflib
    libusb
    python37Packages.pyusb
    python37Packages.matplotlib
  ];

in
  nixpkgs.stdenv.mkDerivation {
    name = "env";
    buildInputs = pkgs;
  }
