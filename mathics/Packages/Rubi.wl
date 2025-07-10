(* Shim code to run Rubi from Mathics3/Mathics3-Rubi repository *)
Rubi`$RubiDir = FileNameJoin[{$BaseDirectory, "Packages", "Rubi"}];
RubiProgram = FileNameJoin[{Rubi`$RubiDir, "Rubi.m"}];
IntegrationTestProgram`$IntegrationProgramDir = Rubi`$RubiDir;
Get[RubiProgram]
