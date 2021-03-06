{ pkgs, stdenv, fetchFromGitHub, python, fetchPypi}:

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
    src = fetchPypi {
      inherit pname version;
      sha256 = "1h0b6b0nng6f845jrzx7f2dhfir3pngm0dh1hh67cyalw6gahssl";
    };
  }
