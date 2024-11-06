{ config, pkgs, ... }:

{
  environment.systemPackages = with pkgs; [
    (writeScriptBin "ca" ''
      #!${pkgs.bash}/bin/bash
      ${pkgs.python3}/bin/python3 /PATH/TO/nixos-scan-packages/search-nixos-packages.py "$@"
    '')
  ];
}
