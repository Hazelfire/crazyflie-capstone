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
      rev = "acdcfd005cbd7d6d3ed6e1a41aa6fc54c987ca35";
      sha256 = "0rw6i1rlrn3fkb9l3ddz0vh9jbblx0dl67n21pm0arcijdqrk31a";
    };
  }
