# [OpenCSGO](https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive)

![CS:GO](https://developer.valvesoftware.com/w/images/2/23/SoftwareCover-Counter-Strike_Global_Offensive.jpg)

This project is aimed to improve the leaked CS:GO code, to make it more stable and to make it playable.
Use resources from CS:S to get the HUD and GameUI to work properly.

Partially used code from [Kisak-Strike](https://github.com/SwagSoftware/Kisak-Strike) (some econ stuff, weapon recoil).

Features:
- Removed Scaleform;
- Filesystem from TF2 leak (less hardcoded stuff, allows for 'custom' folder, etc);
- Some VGUI stuff and complete GameUI ported from TF2 leak;

Currently known bugs:
- sv_pure is most likely broken due to differences between CS:GO and TF2 implementations that I was
  too lazy to fix for TF2 filesystem at 6AM, just 2 hours before going to college with no sleep;
- Game currently crashes after shutting down (something related to g_pCVar and outputting console messages,
  I think g_pCVar gets destructed before it is used for outputting console messages or something);
