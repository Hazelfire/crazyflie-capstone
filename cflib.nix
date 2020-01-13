{ pkgs, stdenv, fetchFromGitHub, python }:

let
  pyPackages = py: with py; [
    pyusb
  ];

in
  python.pkgs.buildPythonPackage rec {
    pname = "cflib";
    version = "0.1.8";
    buildInputs = [ python.pkgs.pyusb ];
    doCheck = false;
    src = fetchFromGitHub {
      owner = "bitcraze";
      repo = "crazyflie-lib-python";
      rev = "${version}";
      sha256 = "0070frdy18vlkgn86xkf3z54q22j4nai0bq8bkiq6l35kmj7w1gk";
    };
  }
