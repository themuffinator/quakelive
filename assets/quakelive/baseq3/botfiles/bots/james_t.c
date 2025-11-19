//===========================================================================
//
// Name:			james_c.c
// Function:		chat lines for James
// Programmer:	Mr. Elusive
// Scripter:		Adam Pyle
// Chat:			Courtesy of the Elder Scrolls
//===========================================================================

chat "james"
{
	#include "teamplay.h"
	//
	type "game_enter"
	{
		"Hail citizen!";
		"Hey! I know you.";
		"Good day, citizen.";
	} //end type

	type "game_exit"
	{
		"I wonder how the Thalmor are feeling now that they've been taken down a notch.";
		"Duty calls.";
	} //end type

	type "level_start"
	{
		"I have a bad feeling about this.";
		"YOU SHOULD NEVER HAVE COME HERE";
	} //end type

	type "level_end"
	{
		"What you learn here will last you a lifetime. Several, if you're lucky.";
	} //end type

	type "level_end_victory"
	{
		"Smart man. Now come along with me. We'll take any stolen goods you have and you'll be free to go. After you pay the fine, of course.";
		"It is truly an honor.";
	} //end type

	type "level_end_lose"
	{
		"I used to be a contender like you, but then I took an arrow in the knee.";
	} //end type

	//======================================================
	//======================================================
	type "hit_talking" //bot is hit while chat balloon is visible; lecture attacker on poor sportsmanship
	{
		"A guard could get nervous, someone approaching with their weapon drawn.";
		"I must be hearing things.";
		"What do you need, citizen?";
		"You have my ear, citizen.";
		"Keep moving, scum!";
		//0 = shooter
	} //end type

	type "hit_nodeath" //bot is hit by an opponent's weapon attack; either praise or insult
	{
		"Disrespect the law, and you disrespect me.";
		//0 = shooter
	} //end type

	type "hit_nokill" //bot hits an opponent but does not kill it
	{
		"That's a fine shield you have there. Dwarven isn't it?";
		"STOP RIGHT THERE CRIMINAL SCUM!";
		"Then pay with your sparks!";
		"Stop! You have violated the law! Pay the court a fine or serve your sentence.";
		//0 = opponent
	} //end type

	//================================================================
	//================================================================

	type "death_telefrag"
	{
		"Watch the skies, traveller.";
	} //end type

	type "death_lava"
	{

	} //end type

	type "death_slime"
	{

	} //end type

	type "death_drown"
	{
		"Lightly armoured means light in your feet. Smart.";
	} //end type

	type "death_suicide"
	{

	} //end type 

	type "death_gauntlet"
	{
		"If I find your hand in my pocket, I'm going to cut it off." ;
		"You are like me then. You don't fancy those big clunky two-handed weapons.";
		"Now that's a fine sword you have there, like a sliver of midnight.";
	} //end type

	type "death_rail"
	{
	
	} //end type 

	type "death_bfg"
	{

	} //end type

	type "death_insult"
	{
		"I find your wolfish grin... unsettling.";
	} //end type

	type "death_praise"
	{
		"I've never seen anything quite like this before.";
		"The guards have been talking about you.";
		"By the gods, I dont know what to say.";

	} //end type

		type "death_kamikaze" //initiated when the bot is killed by kamikaze blast
	{
		"So you can cast a few spells, am I supposed to be impressed?";
		"Go cast your fancy magic somewhere else.";
		"How did you come to possess such a rare treasure?";
		// 0 = enemy name
	} //end type 


	//======================================================
	//======================================================

	type "kill_kamikaze" //initiated when the bot kills someone with kamikaze
	{
		"I got to thinking, maybe I'm the Dragonborn, and I just don't know it yet.";
		// 0 = enemy name
	} //end type

	type "kill_rail" 
	{

	} //end type

	type "kill_gauntlet"
	{
		"You come to me wearing Imperial armor?! Do you have steel for brains?";
	} //end type

	type "kill_telefrag"
	{
		"No lollygaggin'.";
	} //end type

	type "kill_insult"
	{
		"Let me guess, someone stole your sweetroll.";
		"Hands to yourself, sneak thief.";
		"Someone's been murdered!";
	} //end type

	type "kill_praise"
	{
		"Not bad, kid. Most don't last that long.";
		"Almost didn't get you there, kid.";
		PRAISE4;
	} //end type

	//================================================================
	//================================================================

	type "random_insult"
	{
		"Heard about you and your honeyed words.";
		"Is that...fur? Coming out of your ears?";
	} //end type

	type "random_misc"
	{
		"My cousin is out fighting dragons, and what do I get? Guard duty.";
		"Go fiddling with any locks around here, and we're going to have a real problem.";
		"You see those warriors in Hammerfall? They've got curved swords. Curved. Swords.";
		"I am sworn to carry your burdens.";
		"Do you get to the Cloud District very often? Oh what am I saying, of course you don't...";
	} //end type

} //end chat visor
