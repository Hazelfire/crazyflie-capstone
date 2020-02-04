{ pkgs, stdenv, fetchFromGitHub, python, fetchPypi}:

let
  pyPackages = py: with py; [
    pyusb
  ];

in
  python.pkgs.buildPythonPackage rec {
    pname = "openvr";
    version = "1.9.1601";
    buildInputs = [ python.pkgs.pyusb ];
    doCheck = false;
    src = fetchPypi {
      inherit pname version;
      sha256 = "029qn4275vy4s0clsippmdf6cs0p2kmw3x9ybxbr16vm1f92624a";
    };
  }
