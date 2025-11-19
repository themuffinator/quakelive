// The sky overheard	-	By Geit (modification of id shader)
textures/geit/geit3ctf2_sky2
{
	qer_editorimage textures/skies/dimclouds.tga
	surfaceparm noimpact
	surfaceparm nomarks
	surfaceparm nolightmap
	q3map_sunExt 0.25 0.25 1 65 200 75 3 16
	q3map_surfacelight 150
	skyparms - 512 -

	{
		map textures/skies/dimclouds.tga
		tcMod scroll 0.0001 0
		tcMod scale 2 2
		depthWrite
	}
}

// Dusty beam in the dark passage
textures/geit/geit3ctf2_beam
{
    qer_editorimage textures/geit/geit3ctf2_beam.tga
	surfaceparm trans	
    surfaceparm nomarks	
    surfaceparm nonsolid
	surfaceparm nolightmap
    qer_trans .6
	cull none
	{
		map textures/geit/geit3ctf2_beam.tga
		tcMod Scroll .3 0
        blendFunc add
    }
}

textures/geit/butterfly1
{
	qer_editorimage textures/geit/butterfly-1.tga
	surfaceparm nodamage
	surfaceparm noimpact
	surfaceparm nolightmap
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm trans
	deformVertexes wave 11.3 sin 0 8 0 5 
	deformVertexes move 4 4 4 sin 0 1 0.75 0.5 
	tessSize 16
    cull disable
	nopicmip
	{
		map textures/geit/butterfly-1.tga
		blendfunc blend
		rgbGen identity
	}
}
textures/geit/vine_hedge
{	
    qer_editorimage textures/geit/vine_hedge.tga
	surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	cull none
    nopicmip
	{
		map textures/geit/vine_hedge.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}