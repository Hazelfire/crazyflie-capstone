{lib, pkgs, stdenv, fetchFromGitHub, python, fetchPypi}:

let
  cflib = pkgs.python.pkgs.callPackage ./cflib.nix {python=pkgs.python3;};
  openvr = pkgs.python.pkgs.callPackage ./openvr.nix {python=pkgs.python3;};
  nix-gitignore = pkgs.callPackage (pkgs.fetchFromGitHub{
    owner = "siers";
    repo= "nix-gitignore";
    rev = "a4ce20ba415175c77e5ae70461641a57d7527b2f";
    sha256 = "0i3szbwrynxgvl55qqlzsa040fqd0cnx84bpydai6mdrrsvnj1cg";
  }) {};

in
  python.pkgs.buildPythonPackage rec {
    pname = "cfdemos";
    version = "0.1";
    propagatedBuildInputs = [ cflib openvr ];
    doCheck = false;
    src = nix-gitignore.gitignoreSource [] ./.;
}
