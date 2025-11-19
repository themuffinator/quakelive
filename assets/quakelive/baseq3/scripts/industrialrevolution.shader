textures/industrialrevolution/fog
{
	qer_editorimage textures/phantq3dm3/tp_fog.tga
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nolightmap
	surfaceparm fog
	fogparms ( 0.4823529 0.5294117 0.3333333 ) 1000
}

textures/industrialrevolution/nodraw_liquid
{
	surfaceparm nodraw
	surfaceparm nonsolid
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm water
}


textures/industrialrevolution/bubble_a
{
	qer_editorimage textures/industrialrevolution/bubble.tga
	sort underwater
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	deformVertexes autosprite
	deformVertexes move 0 0 148 sawtooth 0 1 0 1

	{
		map sprites/bubble.tga
		blendFunc add
		rgbGen vertex
		alphaGen vertex
	}
}


textures/industrialrevolution/bubble_b
{
	qer_editorimage textures/industrialrevolution/bubble.tga
	sort underwater
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	deformVertexes autosprite
	deformVertexes move 0 0 148 sawtooth 0 1 0.2 1.1

	{
		map sprites/bubble.tga
		blendFunc add
		rgbGen vertex
		alphaGen vertex
	}
}


textures/industrialrevolution/bubble_c
{
	qer_editorimage textures/industrialrevolution/bubble.tga
	sort underwater
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	deformVertexes autosprite
	deformVertexes move 0 0 148 sawtooth 0 1 0.4 1.2

	{
		map sprites/bubble.tga
		blendFunc add
		rgbGen vertex
		alphaGen vertex
	}
}


textures/industrialrevolution/bubble_d
{
	qer_editorimage textures/industrialrevolution/bubble.tga
	sort underwater
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	deformVertexes autosprite
	deformVertexes move 0 0 148 sawtooth 0 1 0.6 0.9

	{
		map sprites/bubble.tga
		blendFunc add
		rgbGen vertex
		alphaGen vertex
	}
}


textures/industrialrevolution/bubble_e
{
	qer_editorimage textures/industrialrevolution/bubble.tga
	sort underwater
	cull none
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	deformVertexes autosprite
	deformVertexes move 0 0 148 sawtooth 0 1 0.8 0.8

	{
		map sprites/bubble.tga
		blendFunc add
		rgbGen vertex
		alphaGen vertex
	}
}


textures/industrialrevolution/proto_light_noflicker
{
	q3map_lightimage textures/base_light/proto_lightmap.tga
	qer_editorimage textures/base_light/proto_light.tga
	//surfaceparm nomarks
	q3map_surfacelight 1000

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/base_light/proto_light.tga
		blendFunc filter
		rgbGen identity
	}

	{	
		map textures/base_light/proto_lightmap.tga
		blendfunc GL_ONE GL_ONE
	}

	{	
		map textures/base_light/proto_light2.tga
		blendfunc GL_ONE GL_ONE
	}
}


// basically like many id sky shaders
textures/industrialrevolution/revsky
{
	// de-yellowize the sky light ... I'm using a bit of ambient yellow
	q3map_lightimage textures/common/white.tga
	qer_editorimage textures/skies/inteldimredclouds.tga

	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_globaltexture
	q3map_lightsubdivide 512 
	q3map_sunExt 0.25 0.25 0.20 75 0 75 3 16
	q3map_surfacelight 200
	q3map_backsplash 0 256

	skyparms - 512 -
	
	{
		map textures/skies/inteldimclouds.tga
		tcMod scroll 0.05 0.025
		tcMod scale 3 2
		depthWrite
	}

	{
		map textures/skies/intelredclouds.tga
		blendFunc GL_ONE GL_ONE
		tcMod scroll 0.05 0.05
		tcMod scale 3 3
	}
}


textures/industrialrevolution/q3hh1_1_th_trim06_lit
{
	qer_editorimage textures/industrialrevolution/q3hh1_1_th_trim06.tga
	q3map_surfacelight 500

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1_th_trim06.tga
		blendfunc filter
		rgbgen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1_th_trim06_glo.tga
		blendfunc add
		rgbgen const ( 0.75 0.75 0.75 )
	}
}


textures/industrialrevolution/q3hh1_1r_metpan05_r_lit_0
{
	q3map_lightimage textures/industrialrevolution/redglowbig.tga
	q3map_surfacelight 100
	q3map_lightsubdivide 60

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05.tga
		blendfunc filter
		rgbgen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05_rglo.tga
		blendfunc add
		rgbGen wave sin 0.6 0.2 0.833 0.25
	}
}


textures/industrialrevolution/q3hh1_1r_metpan05_r_lit_1
{
	q3map_lightimage textures/industrialrevolution/redglowbig.tga
	q3map_surfacelight 100
	q3map_lightsubdivide 60

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05.tga
		blendfunc filter
		rgbgen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05_rglo.tga
		blendfunc add
		rgbGen wave sin 0.6 0.2 0.666 0.25
	}
}


textures/industrialrevolution/q3hh1_1r_metpan05_r_lit_2
{
	q3map_lightimage textures/industrialrevolution/redglowbig.tga
	q3map_surfacelight 100
	q3map_lightsubdivide 60

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05.tga
		blendfunc filter
		rgbgen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05_rglo.tga
		blendfunc add
		rgbGen wave sin 0.6 0.2 0.499 0.25
	}
}


textures/industrialrevolution/q3hh1_1r_metpan05_r_lit_3
{
	q3map_lightimage textures/industrialrevolution/redglowbig.tga
	q3map_surfacelight 100
	q3map_lightsubdivide 60

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05.tga
		blendfunc filter
		rgbgen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05_rglo.tga
		blendfunc add
		rgbGen wave sin 0.6 0.2 0.332 0.25
	}
}


textures/industrialrevolution/q3hh1_1r_metpan05_r_lit_4
{
	q3map_lightimage textures/industrialrevolution/redglowbig.tga
	q3map_surfacelight 100
	q3map_lightsubdivide 60

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05.tga
		blendfunc filter
		rgbgen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05_rglo.tga
		blendfunc add
		rgbGen wave sin 0.6 0.2 0.165 0.25
	}
}


textures/industrialrevolution/q3hh1_1r_metpan05_r_lit_5
{
	q3map_lightimage textures/industrialrevolution/redglowbig.tga
	q3map_surfacelight 100
	q3map_lightsubdivide 60

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05.tga
		blendfunc filter
		rgbgen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05_rglo.tga
		blendfunc add
		rgbGen wave sin 0.6 0.2 0 0.25
	}
}


textures/industrialrevolution/q3hh1_1r_metpan05_b_lit_0
{
	q3map_lightimage textures/industrialrevolution/blueglowbig.tga
	q3map_surfacelight 100
	q3map_lightsubdivide 60

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05.tga
		blendfunc filter
		rgbgen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05_bglo.tga
		blendfunc add
		rgbGen wave sin 0.6 0.2 0.833 0.25
	}
}


textures/industrialrevolution/q3hh1_1r_metpan05_b_lit_1
{
	q3map_lightimage textures/industrialrevolution/blueglowbig.tga
	q3map_surfacelight 100
	q3map_lightsubdivide 60

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05.tga
		blendfunc filter
		rgbgen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05_bglo.tga
		blendfunc add
		rgbGen wave sin 0.6 0.2 0.666 0.25
	}
}


textures/industrialrevolution/q3hh1_1r_metpan05_b_lit_2
{
	q3map_lightimage textures/industrialrevolution/blueglowbig.tga
	q3map_surfacelight 100
	q3map_lightsubdivide 60

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05.tga
		blendfunc filter
		rgbgen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05_bglo.tga
		blendfunc add
		rgbGen wave sin 0.6 0.2 0.499 0.25
	}
}


textures/industrialrevolution/q3hh1_1r_metpan05_b_lit_3
{
	q3map_lightimage textures/industrialrevolution/blueglowbig.tga
	q3map_surfacelight 100
	q3map_lightsubdivide 60

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05.tga
		blendfunc filter
		rgbgen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05_bglo.tga
		blendfunc add
		rgbGen wave sin 0.6 0.2 0.332 0.25
	}
}


textures/industrialrevolution/q3hh1_1r_metpan05_b_lit_4
{
	q3map_lightimage textures/industrialrevolution/blueglowbig.tga
	q3map_surfacelight 100
	q3map_lightsubdivide 60

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05.tga
		blendfunc filter
		rgbgen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05_bglo.tga
		blendfunc add
		rgbGen wave sin 0.6 0.2 0.165 0.25
	}
}


textures/industrialrevolution/q3hh1_1r_metpan05_b_lit_5
{
	q3map_lightimage textures/industrialrevolution/blueglowbig.tga
	q3map_surfacelight 100
	q3map_lightsubdivide 60

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05.tga
		blendfunc filter
		rgbgen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_metpan05_bglo.tga
		blendfunc add
		rgbGen wave sin 0.6 0.2 0 0.25
	}
}


textures/industrialrevolution/q3hh1_1_th_trim03_r_lit
{
	q3map_lightimage textures/industrialrevolution/redglow.tga
	qer_editorimage textures/industrialrevolution/q3hh1_1_th_trim03_r.tga
	q3map_surfacelight 100
	q3map_lightsubdivide 60

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1_th_trim03.tga
		blendfunc filter
		rgbgen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1_th_trim03_rglo.tga
		blendfunc add
		rgbGen wave sin 0.7 0.1 0 0.5
	}
}


textures/industrialrevolution/q3hh1_1_th_trim03_b_lit
{
	q3map_lightimage textures/industrialrevolution/blueglow.tga
	qer_editorimage textures/industrialrevolution/q3hh1_1_th_trim03_b.tga
	q3map_surfacelight 100
	q3map_lightsubdivide 60

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1_th_trim03.tga
		blendfunc filter
		rgbgen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1_th_trim03_bglo.tga
		blendfunc add
		rgbGen wave sin 0.7 0.1 0 0.5
	}
}


textures/industrialrevolution/q3hh1_1r_light01_3k
{
	qer_editorimage textures/industrialrevolution/q3hh1_1r_light01_mod.tga
	q3map_surfacelight 3000

	{
		map $lightmap
		rgbGen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_light01_mod.tga
		blendfunc filter
		rgbgen identity
	}

	{
		map textures/industrialrevolution/q3hh1_1r_light01_modglo.tga
		blendfunc add
		rgbgen const ( 0.65 0.65 0.65 )
	}
}


textures/industrialrevolution/holey_grate
{
	qer_editorimage textures/industrialrevolution/q3hh1_1r_floor03.tga
	surfaceparm trans

	{
		map textures/industrialrevolution/q3hh1_1r_floor03.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}

	{
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}


textures/industrialrevolution/fan_newgrate
{
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid	
	//cull none
	//nopicmip

	{
		map textures/industrialrevolution/fan_newgrate.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}

	{
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}


textures/industrialrevolution/redlift_glow_green
{
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm nolightmap
	//cull none
	//nopicmip
	polygonOffset

	{
		map textures/industrialrevolution/newgrate_glow_green.jpg
		blendfunc add
		rgbgen wave triangle 1 5 1 3
	}

	{
		map textures/industrialrevolution/newgrate_glow_green.jpg
		blendfunc add
		rgbgen wave triangle 1 2 0 7
	}
}


textures/industrialrevolution/redlift_glow_yellow
{
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm nolightmap
	//cull none
	//nopicmip
	polygonOffset

	{
		map textures/industrialrevolution/newgrate_glow_yellow.jpg
		blendfunc add
		rgbGen wave square 0 1 0 1
	}
}


textures/industrialrevolution/bluelift_glow_green
{
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm nolightmap
	//cull none
	//nopicmip
	polygonOffset

	{
		map textures/industrialrevolution/newgrate_glow_green.jpg
		blendfunc add
		rgbgen wave triangle 1 5 1 3
	}

	{
		map textures/industrialrevolution/newgrate_glow_green.jpg
		blendfunc add
		rgbgen wave triangle 1 2 0 7
	}
}


textures/industrialrevolution/bluelift_glow_yellow
{
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	surfaceparm nolightmap
	//cull none
	//nopicmip
	polygonOffset

	{
		map textures/industrialrevolution/newgrate_glow_yellow.jpg
		blendfunc add
		rgbGen wave square 0 1 0 1
	}
}


textures/industrialrevolution/fan_newgrate_solid
{
	qer_editorimage textures/industrialrevolution/fan_newgrate.tga
	surfaceparm trans
	surfaceparm metalsteps
	//cull none
	//nopicmip

	{
		map textures/industrialrevolution/fan_newgrate.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}

	{
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}


textures/industrialrevolution/fan_newgrate_closed
{
	surfaceparm metalsteps

	{
		map textures/industrialrevolution/fan_newgrate_closed.tga
		rgbGen identity
	}

	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}


textures/industrialrevolution/newgrate
{
	surfaceparm metalsteps

	{
		map textures/industrialrevolution/newgrate.tga
		rgbGen identity
	}

	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}


textures/industrialrevolution/hardblack
{
	surfaceparm nolightmap
	surfaceparm nomarks

	{
		map textures/industrialrevolution/id_sfx_blackness.tga
	}
}

// From the id sfx shader, made it faster and synched with
// the noise; other tweaks.
textures/industrialrevolution/fan
{
	qer_editorimage textures/sfx/fan
	surfaceparm trans
	surfaceparm nomarks
	surfaceparm nonsolid
	//cull none
	//nopicmip

	{
		clampmap textures/sfx/fan.tga
		tcMod rotate 495
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthWrite
		rgbGen identity
	}

	{
		map $lightmap
		rgbGen identity
		blendFunc filter
		depthFunc equal
	}
}


textures/industrialrevolution/powdisk_disabled
{
	qer_editorimage textures/industrialrevolution/q3hh1_1r_cog01.tga
	surfaceparm trans

	{
	map textures/industrialrevolution/q3hh1_1r_cog01.tga
	alphaFunc GE128
	depthWrite
	rgbGen identity
	}

	{
	map $lightmap
	rgbGen identity
	blendFunc filter
	depthFunc equal
	}
}


// Clampmap doesn't seem to work when this is applied to the mesh,
// so I have to make the texture larger and add a blank buffer
// around the image... sigh.
textures/industrialrevolution/powdisk_red
{
	qer_editorimage textures/industrialrevolution/q3hh1_1r_cog01.tga
	surfaceparm trans
	surfaceparm nomarks

	{
	map textures/industrialrevolution/q3hh1_1r_cog01.tga
	tcMod rotate 50
	alphaFunc GE128
	depthWrite
	rgbGen identity
	}

	{
	map $lightmap
	rgbGen identity
	blendFunc filter
	depthFunc equal
	}

	{
	map textures/industrialrevolution/powdisk_glow_red.tga
	tcMod transform 2 0 0 2 -0.5 -0.5
	tcMod rotate 50
	rgbGen wave sin 0 0.75 0 1
	blendFunc add
	}
}


// Clampmap doesn't seem to work when this is applied to the mesh,
// so I have to make the texture larger and add a blank buffer
// around the image... sigh.
textures/industrialrevolution/powdisk_blue
{
	qer_editorimage textures/industrialrevolution/q3hh1_1r_cog01.tga
	surfaceparm trans
	surfaceparm nomarks

	{
	map textures/industrialrevolution/q3hh1_1r_cog01.tga
	tcMod rotate 50
	alphaFunc GE128
	depthWrite
	rgbGen identity
	}

	{
	map $lightmap
	rgbGen identity
	blendFunc filter
	depthFunc equal
	}

	{
	map textures/industrialrevolution/powdisk_glow_blue.tga
	tcMod transform 2 0 0 2 -0.5 -0.5
	tcMod rotate 50
	rgbGen wave sin 0 0.75 0 1
	blendFunc add
	}
}


// proto_fence as nonsolid

textures/industrialrevolution/proto_fence
{
        qer_editorimage textures/base_trim/proto_fence.tga
        surfaceparm trans
        surfaceparm nonsolid
        surfaceparm nomarks
        cull none
        nopicmip

        {
                map textures/base_trim/proto_fence.tga
                tcMod scale 3 3
                blendFunc GL_ONE GL_ZERO
                alphaFunc GE128
                depthWrite
                rgbGen identity
        }

        {
                map $lightmap
                rgbGen identity
                blendFunc filter
                depthFunc equal
        }
}


// CTF Unified shaders

textures/industrialrevolution/ctfu_direction_blue
{    
	surfaceparm nomarks   
	surfaceparm trans
	surfaceparm pointlight
   
	{
		map textures/industrialrevolution/ctfu_direction_blue.tga
                blendFunc add
		rgbGen vertex
	}
}


textures/industrialrevolution/ctfu_direction_red
{    
	surfaceparm nomarks 
	surfaceparm trans  
	surfaceparm pointlight
        
	{
		map textures/industrialrevolution/ctfu_direction_red.tga
                blendFunc add
		rgbGen vertex
	}
}


textures/industrialrevolution/ctfu_weapfloor_neutral
{
	qer_editorimage textures/industrialrevolution/ctfu_weapfloor_fx.tga
//	surfaceparm alphashadow
	surfaceparm metalsteps
	surfaceparm nomarks
	surfaceparm trans

	{
		clampmap textures/industrialrevolution/ctfu_weapfloor_fx.tga
		rgbGen wave sin 0.9 0.2 0 0.7
		tcMod rotate 180
		depthWrite
		alphaFunc GE128
	}
	{
		map textures/industrialrevolution/ctfu_weapfloor_1.tga
		blendfunc blend
		rgbGen identity
		depthFunc equal
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
		tcGen lightmap
		depthFunc equal
	}
	{
		map textures/industrialrevolution/ctfu_weapfloor_shadow.tga
		blendfunc filter
		rgbGen identity
	}
}


textures/industrialrevolution/ctfu_weapfloor_blue
{
	qer_editorimage textures/industrialrevolution/ctfu_weapfloor_fx_blue.tga
//	surfaceparm alphashadow
	surfaceparm metalsteps
	surfaceparm nomarks
	surfaceparm trans

	{
		clampmap textures/industrialrevolution/ctfu_weapfloor_fx_blue.tga
		rgbGen wave sin 0.9 0.2 0 0.7
		tcMod rotate 180
		depthWrite
		alphaFunc GE128
	}
	{
		map textures/industrialrevolution/ctfu_weapfloor_1.tga
		blendfunc blend
		rgbGen identity
		depthFunc equal
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
		tcGen lightmap
		depthFunc equal
	}
	{
		map textures/industrialrevolution/ctfu_weapfloor_shadow.tga
		blendfunc filter
		rgbGen identity
	}
}


textures/industrialrevolution/ctfu_weapfloor_red
{
	qer_editorimage textures/industrialrevolution/ctfu_weapfloor_fx_red.tga
//	surfaceparm alphashadow
	surfaceparm metalsteps
	surfaceparm nomarks
	surfaceparm trans

	{
		clampmap textures/industrialrevolution/ctfu_weapfloor_fx_red.tga
		rgbGen wave sin 0.9 0.2 0 0.7
		tcMod rotate 180
		depthWrite
		alphaFunc GE128
	}
	{
		map textures/industrialrevolution/ctfu_weapfloor_1.tga
		blendfunc blend
		rgbGen identity
		depthFunc equal
	}
	{
		map $lightmap
		blendfunc filter
		rgbGen identity
		tcGen lightmap
		depthFunc equal
	}
	{
		map textures/industrialrevolution/ctfu_weapfloor_shadow.tga
		blendfunc filter
		rgbGen identity
	}
}


textures/industrialrevolution/ctfu_monologo_flash_blue
{       	
	qer_editorimage textures/industrialrevolution/ctfu_floor_monologo_blue.tga
	qer_trans 0.4
	surfaceparm nolightmap
	surfaceparm nomarks
	surfaceparm trans
	cull none

	{
		map textures/industrialrevolution/ctfu_floor_monologo_blue.tga
		blendFunc Add
		rgbGen wave sin 1 .5 0 .2
	}
}


textures/industrialrevolution/ctfu_monologo_flash_red
{       	
	qer_editorimage textures/industrialrevolution/ctfu_floor_monologo_red.tga
	qer_trans 0.4
	surfaceparm nolightmap
	surfaceparm nomarks
	surfaceparm trans
	cull none

	{
		map textures/industrialrevolution/ctfu_floor_monologo_red.tga
		blendFunc Add
		rgbGen wave sin 1 .5 0 .2
	}
}


textures/industrialrevolution/ctfu_floor_decal_blue
{       	
	qer_editorimage textures/industrialrevolution/ctfu_floor_logo_blue.tga
	qer_trans 0.4
	surfaceparm nolightmap
	surfaceparm pointlight
	surfaceparm nomarks
	surfaceparm trans
	cull none

	{
		map textures/industrialrevolution/ctfu_floor_logo_blue.tga
		blendFunc blend
		rgbgen vertex
		depthWrite
	}
}


textures/industrialrevolution/ctfu_floor_decal_red
{       	
	qer_editorimage textures/industrialrevolution/ctfu_floor_logo_red.tga
	qer_trans 0.4
	surfaceparm nolightmap
	surfaceparm pointlight
	surfaceparm nomarks
	surfaceparm trans
	cull none

	{
		map textures/industrialrevolution/ctfu_floor_logo_red.tga
		blendFunc blend
		rgbgen vertex
		depthWrite
	}
}


textures/industrialrevolution/ctfu_ta_techspawn_blue
{
	qer_editorimage textures/industrialrevolution/ctfu_tech_fx_blue.tga
	surfaceparm nonsolid

	{
		clampmap textures/industrialrevolution/ctfu_tech_fx_blue.tga
		rgbGen identity
		tcMod rotate 222
	}
	{
		clampmap textures/industrialrevolution/ctfu_tech.tga
		blendfunc gl_one gl_one_minus_src_alpha
		rgbGen Vertex
	}
}


textures/industrialrevolution/ctfu_ta_techspawn_red
{
	qer_editorimage textures/industrialrevolution/ctfu_tech_fx_red.tga
	surfaceparm nonsolid

	{
		clampmap textures/industrialrevolution/ctfu_tech_fx_red.tga
		rgbGen identity
		tcMod rotate 222
	}
	{
		clampmap textures/industrialrevolution/ctfu_tech.tga
		blendfunc blend
		rgbGen Vertex
	}
}


// Slightly modifed CTF Unified logo shaders (alternate phases)

textures/industrialrevolution/ctfu_logo_b_alt
{       	
	qer_editorimage textures/industrialrevolution/ctfu_floor_monologo_blue.tga
	qer_trans 0.4
	surfaceparm nolightmap
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm nonsolid
	cull none

	{
		map textures/industrialrevolution/ctfu_floor_monologo_blue.tga
		blendFunc Add
		rgbGen wave sin .5 .5 0 .2
	}
}


textures/industrialrevolution/ctfu_logo_r_alt
{       	
	qer_editorimage textures/industrialrevolution/ctfu_floor_monologo_red.tga
	qer_trans 0.4
	surfaceparm nolightmap
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm nonsolid
	cull none

	{
		map textures/industrialrevolution/ctfu_floor_monologo_red.tga
		blendFunc Add
		rgbGen wave sin .5 .5 0.5 .2
	}
}


// ctf_unified banners, no motion

textures/industrialrevolution/ctfu_banner01_blue
{
	qer_editorimage textures/industrialrevolution/ctfu_banner01_blue.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm alphashadow
	cull none
//	tessSize 64
//	deformVertexes wave 194 sin 0 3 0 .4
//	deformVertexes normal .3 .2

	{
		map textures/industrialrevolution/ctfu_banner01_blue.tga
		rgbGen identity
	}
	{
		map $lightmap
		blendFunc filter
		rgbGen identity
	}
//	{
//		map textures/sfx/shadow.tga
//		tcGen environment
//		blendFunc filter
//		rgbGen identity
//	}
}

textures/industrialrevolution/ctfu_banner01_red
{
	qer_editorimage textures/industrialrevolution/ctfu_banner01_red.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm alphashadow
	cull none
//	tessSize 64
//	deformVertexes wave 194 sin 0 3 0 .4
//	deformVertexes normal .3 .2

	{
		map textures/industrialrevolution/ctfu_banner01_red.tga
		rgbGen identity
	}
	{
		map $lightmap
		blendFunc filter
		rgbGen identity
	}
//	{
//		map textures/sfx/shadow.tga
//		tcGen environment
//		blendFunc filter
//		rgbGen identity
//	}
}


// Using the banner textures for thin ribbons that flap rapidly.

textures/xxxx2010jlctf3/redribbon
{
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm nolightmap
	cull none
	deformVertexes wave 32 sin 0 2 0 6
	deformVertexes wave 45 sin 0 2 0.5 6

	{
		map textures/ctf/ctf_redflag2.tga
		rgbGen lightingDiffuse
	}
}


textures/xxxx2010jlctf3/blueribbon
{
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm trans
	surfaceparm nolightmap
	cull none
	deformVertexes wave 32 sin 0 2 0 6
	deformVertexes wave 45 sin 0 2 0.5 6

	{
		map textures/ctf/ctf_blueflag2.tga
		rgbGen lightingDiffuse
	}
}

// non-shadow-casting shaders for the block that plugs the
// flag hole in oneflag and harvester.

textures/industrialrevolution/q3hh1_1r_metpan02_trans
{
	qer_editorimage textures/industrialrevolution/q3hh1_1r_metpan02.tga
	surfaceparm trans

	{
		map textures/industrialrevolution/q3hh1_1r_metpan02.tga
		rgbGen identity
	}

	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

textures/industrialrevolution/q3hh1_1r_metpan02_mod_trans
{
	qer_editorimage textures/industrialrevolution/q3hh1_1r_metpan02_mod.tga
	surfaceparm trans

	{
		map textures/industrialrevolution/q3hh1_1r_metpan02_mod.tga
		rgbGen identity
	}

	{
		map $lightmap
		blendfunc filter
		rgbGen identity
	}
}

textures/industrialrevolution/v_q3hh1_1_th_trim03_b
{
	surfaceparm nolightmap

	{
		map textures/industrialrevolution/v_q3hh1_1_th_trim03_b.tga
		rgbgen vertex
	}
}

textures/industrialrevolution/v_q3hh1_1_th_trim03_r
{
	surfaceparm nolightmap

	{
		map textures/industrialrevolution/v_q3hh1_1_th_trim03_r.tga
		rgbgen vertex
	}
}

textures/industrialrevolution/v_q3hh1_1r_metpan05b
{
	surfaceparm nolightmap

	{
		map textures/industrialrevolution/v_q3hh1_1r_metpan05b.tga
		rgbgen vertex
	}
}

textures/industrialrevolution/v_q3hh1_1r_metpan05_b
{
	surfaceparm nolightmap

	{
		map textures/industrialrevolution/v_q3hh1_1r_metpan05_b.tga
		rgbgen vertex
	}
}

textures/industrialrevolution/v_q3hh1_1r_metpan05_r
{
	surfaceparm nolightmap

	{
		map textures/industrialrevolution/v_q3hh1_1r_metpan05_r.tga
		rgbgen vertex
	}
}
