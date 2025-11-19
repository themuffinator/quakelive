//===========================================================================
//
// Name:			trainer_i.c
// Function:		
// Programmer:		Maleficus
// Tab Size:		4 (real tabs)
//===========================================================================

#include "inv.h"

//initial health/armor states
#define FS_HEALTH				3
#define FS_ARMOR				3

#define W_SHOTGUN				50
#define W_MACHINEGUN			50
#define W_GRENADELAUNCHER		50
#define W_ROCKETLAUNCHER		50
#define W_RAILGUN				50
#define W_BFG10K				50
#define W_LIGHTNING				50
#define W_PLASMAGUN				50

//the bot has the weapons, so the weights change a little bit
#define GWW_SHOTGUN				30
#define GWW_MACHINEGUN			30
#define GWW_GRENADELAUNCHER		30
#define GWW_ROCKETLAUNCHER		30
#define GWW_RAILGUN				30
#define GWW_BFG10K				30
#define GWW_LIGHTNING			30
#define GWW_PLASMAGUN			30

//initial powerup weights
#define W_TELEPORTER			10
#define W_MEDKIT				10
#define W_QUAD					400
#define W_ENVIRO				10
#define W_HASTE					10
#define W_INVISIBILITY			10
#define W_REGEN					10
#define W_FLIGHT				10

//flag weight
#define FLAG_WEIGHT				50

//
#include "fw_items.c"

