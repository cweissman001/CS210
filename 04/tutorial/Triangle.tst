load Triangle.hack,
output-file Triangle.out,
compare-to Triangle.cmp,
output-list RAM[0]%D2.6.2 RAM[1]%D2.6.2;


set PC 0,
set RAM[0] 1,   // Set test arguments
set RAM[1] -1;  // Ensure that program initialized product to 0
repeat 30 {
  ticktock;
}
set RAM[0] 1,   // Restore arguments in case program used them as loop counter
output;

set PC 0,
set RAM[0] 2,   // Set test arguments
set RAM[1] -1;  // Ensure that program initialized product to 0
repeat 50 {
  ticktock;
}
set RAM[0] 2,   // Restore arguments in case program used them as loop counter
output;
set PC 0,
set RAM[0] 5,   // Set test arguments
set RAM[1] -1;  // Ensure that program initialized product to 0
repeat 80 {
  ticktock;
}
set RAM[0] 5,   // Restore arguments in case program used them as loop counter
output;

set PC 0,
set RAM[0] 8,   // Set test arguments
set RAM[1] -1;  // Ensure that program initialized product to 0
repeat 120 {
  ticktock;
}
set RAM[0] 8,   // Restore arguments in case program used them as loop counter
output;
