//GLASS

textures/ct_cure/glass
{
	qer_editorimage textures/ct_cure/shiny3.tga
    surfaceparm trans	
	cull none
	qer_trans 	0.5
	sort 7
     
        {
		map textures/ct_cure/tinfx.tga
                tcgen environment
		blendFunc GL_ONE GL_ONE
		rgbGen identity
	}
        {
		map $lightmap
		rgbGen identity
		blendFunc filter
	}
           
}

textures/ct_cure/lamp_glass
{
	qer_editorimage textures/ct_cure/lamp_glass.tga
        surfaceparm trans	
	cull none
	qer_trans 	0.5
     
        {
		map textures/ct_cure/tinfx.tga
                tcgen environment
		blendFunc GL_ONE GL_ONE
		rgbGen identity
	}
        {
		map $lightmap
		rgbGen identity
		blendFunc filter
	}
           
}

//LIGHTS

textures/ct_cure/white
{
	qer_editorimage textures/ct_cure/white.tga
	surfaceparm nonsolid
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	
	}
	{
		map textures/ct_cure/white.tga
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/ct_cure/light_yellow
{
	qer_editorimage textures/base_light/ceil1_39.tga
	surfaceparm nomarks
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_39.tga
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
	{
		map textures/base_light/ceil1_39.blend.tga
		blendfunc GL_ONE GL_ONE
	}
}

//DECALS

textures/ct_cure/item_marker
{
	qer_editorimage textures/ct_cure/decal_logo.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_cure/decal_logo.tga
		rgbGen identity
		blendFunc add
		tcmod rotate 10
	}
	{
		map textures/ct_cure/decal_inner_ring.tga
		rgbGen identity
		blendFunc add
		tcmod rotate 60
	}
	{
		map textures/ct_cure/decal_outer_ring.tga
		rgbGen identity
		blendFunc add
		tcmod rotate 45
	}
}

textures/ct_cure/decal_inner_ring
{
	qer_editorimage textures/ct_cure/decal_inner_ring.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_cure/decal_inner_ring.tga
		rgbGen identity
		blendFunc add
		tcmod rotate 60
	}
}

textures/ct_cure/decal_outer_ring
{
	qer_editorimage textures/ct_cure/decal_outer_ring.tga
	surfaceparm	nomarks   
    surfaceparm	trans
	surfaceparm	nonsolid
    surfaceparm pointlight
	nopicmip
	{
		map textures/ct_cure/decal_outer_ring.tga
		rgbGen identity
		blendFunc add
		tcmod rotate 45
	}
}



textures/ct_cure/one
{    
     surfaceparm	nomarks   
     surfaceparm	trans
	 surfaceparm	nonsolid
     surfaceparm pointlight
	nopicmip
   
        {
		map textures/ct_cure/one.tga
                blendFunc add
		rgbGen vertex
	}
}

textures/ct_cure/two
{    
     surfaceparm	nomarks   
     surfaceparm	trans
	 surfaceparm	nonsolid
     surfaceparm pointlight
	nopicmip
   
        {
		map textures/ct_cure/two.tga
                blendFunc add
		rgbGen vertex
	}
}
textures/ct_cure/three
{    
     surfaceparm	nomarks   
     surfaceparm	trans
	 surfaceparm	nonsolid
     surfaceparm pointlight
	nopicmip
   
        {
		map textures/ct_cure/three.tga
                blendFunc add
		rgbGen vertex
	}
}

textures/ct_cure/four
{    
     surfaceparm	nomarks   
     surfaceparm	trans
	 surfaceparm	nonsolid
     surfaceparm pointlight
	nopicmip
   
        {
		map textures/ct_cure/four.tga
                blendFunc add
		rgbGen vertex
	}
}

textures/ct_cure/five
{    
     surfaceparm	nomarks   
     surfaceparm	trans
	 surfaceparm	nonsolid
     surfaceparm pointlight
	nopicmip
   
        {
		map textures/ct_cure/five.tga
                blendFunc add
		rgbGen vertex
	}
}

textures/ct_cure/noctis_void_noob
{    
     surfaceparm	nomarks   
     surfaceparm	trans
	 surfaceparm	nonsolid
     surfaceparm pointlight
	nopicmip
   
        {
		map textures/ct_cure/noctis_void_noob.tga
                blendFunc add
		rgbGen vertex
	}
}

//JUMPPAD

textures/ct_cure/wall_jump_wood
{
	qer_editorimage textures/ct_cure/wall_jump_wood.tga

	{
		map textures/sfx2/rlaunch3.tga
		rgbGen identity
		tcmod scale 1 .5
		tcmod scroll 0 1.42
	}

	{
		map textures/ct_cure/wall_jump_wood.tga
		blendFunc blend
		rgbGen identity
	}
	{
		map $lightmap
		rgbGen identity
		blendfunc GL_DST_COLOR GL_ZERO
	}	
}

//FOG

textures/ct_cure/white_fog
{
	qer_editorimage textures/ct_cure/white.tga
	qer_trans .5
	surfaceparm	trans
	surfaceparm	nonsolid
	surfaceparm	fog
	surfaceparm	nolightmap
	qer_nocarve
	fogparms ( .4 .4 .4 ) 1000

}

//SKY

textures/ct_cure/sky
{
	qer_editorimage textures/ct_cure/sky_blue.tga
	surfaceparm noimpact
	surfaceparm nolightmap
	q3map_globaltexture
	surfaceparm sky
	skyparms - 256 -
	
	q3map_sunExt 1 0.932311 0.77821 270 225 80 3 16
	q3map_lightmapFilterRadius 0 12		//self other
	q3map_skyLight 100 3
	
	nopicmip
	nomipmaps
	{
		map textures/ct_cure/sky_blue.tga
		tcMod scale 8 8
		tcMod scroll .02 .02
		depthWrite
	}
	{
		map textures/ct_cure/sky_clouds.tga
		blendFunc GL_ONE GL_ONE
		tcMod scale 4 4
		tcMod scroll 0.01 0.01
	}
} 

// PIE CANDLE
// 128*128 with alpha channel

textures/ct_cure/candle
{
    surfaceparm trans	
	surfaceparm alphashadow
   	surfaceparm nonsolid
	surfaceparm nomarks	
	qer_editorimage textures/ct_cure/candle.tga
	cull none
    nopicmip
	{
		map textures/ct_cure/candle.tga
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