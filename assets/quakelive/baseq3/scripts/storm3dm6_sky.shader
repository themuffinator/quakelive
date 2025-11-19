textures/storm3dm6_sky/env/stormydays
{
	qer_editorimage textures/storm3dm6_sky/skytex.tga
	
	skyParms textures/storm3dm6_sky/env/stormydays - -

	q3map_sun 1 .78 .48 90 225 55	// R G B Intensity Angle Pitch


	q3map_skylight 100 4                    //amount iterations
	q3map_noFog

	surfaceparm sky                         //flags compiler that this is sky
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm nodlight
	nopicmip
	nomipmaps

}
