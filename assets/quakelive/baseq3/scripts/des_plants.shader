textures/des_plants/plant1
{
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm pointlight
	qer_trans 0.99
	deformVertexes wave 16 sin 0 0.5 0 0.1
	{
		map textures/des_plants/plant1.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}

textures/des_plants/plant2
{
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm pointlight
	qer_trans 0.99
	deformVertexes wave 16 sin 0 0.5 0 0.1
	{
		map textures/des_plants/plant2.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}

textures/des_plants/plant3
{
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm pointlight
	qer_trans 0.99
	deformVertexes wave 16 sin 0 0.5 0 0.1
	{
		map textures/des_plants/plant3.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}

textures/des_plants/ivy
{
	qer_editorimage textures/des_plants/ivy.tga
	q3map_cloneShader textures/des_plants/ivy_back
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	qer_trans 0.99
	novlcollapse
	deformVertexes wave 16 sin 0 0.5 0 0.1
	{
		map textures/des_plants/ivy.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}

textures/des_plants/ivy_back
{
	qer_editorimage textures/des_plants/ivy.tga
	q3map_invert
	q3map_vertexScale 0.75
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	qer_trans 0.99
	novlcollapse
	deformVertexes wave 16 sin 0 0.5 0 0.1
	{
		map textures/des_plants/ivy.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/ivy2
{
	qer_editorimage textures/des_plants/ivy2.tga
	q3map_cloneShader textures/des_plants/ivy2_back
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	qer_trans 0.99
	novlcollapse
	deformVertexes wave 16 sin 0 0.5 0 0.1
	{
		map textures/des_plants/ivy2.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}

textures/des_plants/ivy2_back
{
	qer_editorimage textures/des_plants/ivy2.tga
	q3map_invert
	q3map_vertexScale 0.75
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	qer_trans 0.99
	novlcollapse
	deformVertexes wave 16 sin 0 0.5 0 0.1
	{
		map textures/des_plants/ivy2.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/ivy_nosway
{
	qer_editorimage textures/des_plants/ivy.tga
	q3map_cloneShader textures/des_plants/ivy_back_nosway
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	novlcollapse
	qer_trans 0.99
	{
		map textures/des_plants/ivy.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}	
}

textures/des_plants/ivy_back_nosway
{
	qer_editorimage textures/des_plants/ivy.tga
	q3map_invert
	q3map_vertexScale 0.75
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	novlcollapse
	qer_trans 0.99
	{
		map textures/des_plants/ivy.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/ivy2_nosway
{
	qer_editorimage textures/des_plants/ivy2.tga
	q3map_cloneShader textures/des_plants/ivy2_back_nosway
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	novlcollapse
	qer_trans 0.99
	{
		map textures/des_plants/ivy2.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/ivy2_back_nosway
{
	qer_editorimage textures/des_plants/ivy2.tga
	q3map_invert
	q3map_vertexScale 0.75
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	novlcollapse
	qer_trans 0.99
	{
		map textures/des_plants/ivy2.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/lily
{
	surfaceparm alphashadow
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	cull disable
	polygonOffset
	qer_trans 0.99
	q3map_vertexScale 0.75
	deformVertexes wave 64 sin .5 .5 0 .5	
	{
		clampmap textures/des_plants/lily.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		tcmod rotate 7
		depthWrite
		rgbGen exactvertex
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}

textures/des_plants/lilygroup
{
	surfaceparm alphashadow
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	cull disable
	polygonOffset
	qer_trans 0.99
	deformVertexes wave 64 sin .5 .5 0 .5	
	{
		map textures/des_plants/lilygroup.tga
		blendFunc GL_ONE GL_ZERO
		alphaFunc GE128
		depthwrite
		rgbGen exactvertex
	}
	{
		map $lightmap
		rgbGen identity
		blendFunc GL_DST_COLOR GL_ZERO
		depthFunc equal
	}
}

textures/des_plants/reeds
{
	qer_editorimage textures/des_plants/reeds.tga
	q3map_cloneShader textures/des_plants/reeds_back
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm pointlight
	novlcollapse
	nopicmip
	qer_trans 0.99
	sort 7
	deformVertexes wave 16 sin 0 0.5 0 0.1
   	{
		map textures/des_plants/reeds.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/reeds.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/reeds_back
{
	qer_editorimage textures/des_plants/reeds.tga
	q3map_invert
	q3map_vertexScale 1.5
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm pointlight
	novlcollapse
	nopicmip
	qer_trans 0.99
	sort 7
	deformVertexes wave 16 sin 0 0.5 0 0.1
   	{
		map textures/des_plants/reeds.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/reeds.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/reeds_dead
{
	qer_editorimage textures/des_plants/reeds_dead.tga
	q3map_cloneShader textures/des_plants/reeds_dead_back
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm pointlight
	novlcollapse
	nopicmip
	qer_trans 0.99
	sort 7
	deformVertexes wave 16 sin 0 0.5 0 0.1
   	{
		map textures/des_plants/reeds_dead.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/reeds_dead.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/reeds_dead_back
{
	qer_editorimage textures/des_plants/reeds_dead.tga
	q3map_invert
	q3map_vertexScale 1.5
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm pointlight
	novlcollapse
	nopicmip
	qer_trans 0.99
	sort 7
	deformVertexes wave 16 sin 0 0.5 0 0.1
   	{
		map textures/des_plants/reeds_dead.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/reeds_dead.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/reeds_dead2
{
	qer_editorimage textures/des_plants/reeds_dead2.tga
	q3map_cloneShader textures/des_plants/reeds_dead2_back
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm pointlight
	novlcollapse
	nopicmip
	qer_trans 0.99
	sort 7
	deformVertexes wave 16 sin 0 0.5 0 0.1
   	{
		map textures/des_plants/reeds_dead2.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/reeds_dead2.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/reeds_dead2_back
{
	qer_editorimage textures/des_plants/reeds_dead2.tga
	q3map_invert
	q3map_vertexScale 1.5
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm pointlight
	novlcollapse
	nopicmip
	qer_trans 0.99
	sort 7
	deformVertexes wave 16 sin 0 0.5 0 0.1
   	{
		map textures/des_plants/reeds_dead2.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/reeds_dead2.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/vine
{
	surfaceparm nonsolid
	{
		map textures/des_plants/vine.jpg
		rgbGen identity
	}	
	{
		map $lightmap
		blendFunc GL_DST_COLOR GL_ZERO
		rgbGen identity
	}
}

textures/des_plants/leaf_01
{
	qer_editorimage textures/des_plants/leaf_01.tga
	q3map_cloneShader textures/des_plants/leaf_01_back
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
	novlcollapse
	sort 7
   	{
		map textures/des_plants/leaf_01.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/leaf_01.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/leaf_01_back
{
	qer_editorimage textures/des_plants/leaf_01.tga
	q3map_invert
	q3map_vertexScale 3.5
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	qer_trans 0.99
	novlcollapse
	sort 7
   	{
		map textures/des_plants/leaf_01.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/leaf_01.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/leaf_02
{
	qer_editorimage textures/des_plants/leaf_02.tga
	q3map_cloneShader textures/des_plants/leaf_02_back
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
	novlcollapse
	sort 7
   	{
		map textures/des_plants/leaf_02.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/leaf_02.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/leaf_02_back
{
	qer_editorimage textures/des_plants/leaf_02.tga
	q3map_invert
	q3map_vertexScale 3.5
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	qer_trans 0.99
	novlcollapse
	sort 7
   	{
		map textures/des_plants/leaf_02.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/leaf_02.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/leaf_03
{
	qer_editorimage textures/des_plants/leaf_03.tga
	q3map_cloneShader textures/des_plants/leaf_03_back
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
	novlcollapse
	sort 7
   	{
		map textures/des_plants/leaf_03.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/leaf_03.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/leaf_03_back
{
	qer_editorimage textures/des_plants/leaf_03.tga
	q3map_invert
	q3map_vertexScale 3.5
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	qer_trans 0.99
	novlcollapse
	sort 7
   	{
		map textures/des_plants/leaf_03.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/leaf_03.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/leaf_04
{
	qer_editorimage textures/des_plants/leaf_04.tga
	q3map_cloneShader textures/des_plants/leaf_04_back
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
	novlcollapse
	sort 7
   	{
		map textures/des_plants/leaf_04.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/leaf_04.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/leaf_04_back
{
	qer_editorimage textures/des_plants/leaf_04.tga
	q3map_invert
	q3map_vertexScale 3.5
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	qer_trans 0.99
	novlcollapse
	sort 7
   	{
		map textures/des_plants/leaf_04.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/leaf_04.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/leaf_05
{
	qer_editorimage textures/des_plants/leaf_05.tga
	q3map_cloneShader textures/des_plants/leaf_05_back
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
	novlcollapse
	sort 7
   	{
		map textures/des_plants/leaf_05.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/leaf_05.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/leaf_05_back
{
	qer_editorimage textures/des_plants/leaf_05.tga
	q3map_invert
	q3map_vertexScale 3.5
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	qer_trans 0.99
	novlcollapse
	sort 7
   	{
		map textures/des_plants/leaf_05.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/leaf_05.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/leaf_06
{
	qer_editorimage textures/des_plants/leaf_06.tga
	q3map_cloneShader textures/des_plants/leaf_06_back
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
	novlcollapse
	sort 7
   	{
		map textures/des_plants/leaf_06.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/leaf_06.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/leaf_06_back
{
	qer_editorimage textures/des_plants/leaf_06.tga
	q3map_invert
	q3map_vertexScale 3.5
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	qer_trans 0.99
	novlcollapse
	sort 7
   	{
		map textures/des_plants/leaf_06.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/leaf_06.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/leaf_07
{
	qer_editorimage textures/des_plants/leaf_07.tga
	q3map_cloneShader textures/des_plants/leaf_07_back
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
	novlcollapse
	sort 7
   	{
		map textures/des_plants/leaf_07.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/leaf_07.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/leaf_07_back
{
	qer_editorimage textures/des_plants/leaf_07.tga
	q3map_invert
	q3map_vertexScale 3.5
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	qer_trans 0.99
	novlcollapse
	sort 7
   	{
		map textures/des_plants/leaf_07.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/leaf_07.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/bush_leaves
{
	qer_editorimage textures/des_plants/bush_leaves.tga
	q3map_cloneShader textures/des_plants/bush_leaves_back
	q3map_vertexscale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
	{
		map textures/des_plants/bush_leaves.tga
		alphaFunc GE128
		rgbGen vertex
		depthwrite
	}
}

textures/des_plants/bush_leaves_back
{
	qer_editorimage textures/des_plants/bush_leaves.tga
	q3map_invert
	q3map_vertexScale 3.5
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	{
		map textures/des_plants/bush_leaves.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/tree_bark
{
	qer_editorimage textures/des_plants/tree_bark.tga
	q3map_nonplanar
	q3map_shadeangle 90
	{
		map $lightmap
		rgbGen identity
	}
	{
		map textures/des_plants/tree_bark.tga
		blendFunc GL_DST_COLOR GL_ZERO
	}
}

textures/des_plants/tree_leaves
{
	qer_editorimage textures/des_plants/tree_leaves.tga
	q3map_cloneShader textures/des_plants/tree_leaves_back
	q3map_vertexscale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
	novlcollapse
	deformVertexes wave 16 sin 0 1 0 .2
	{
		map textures/des_plants/tree_leaves.tga
		alphaFunc GE128
		rgbGen vertex
		depthwrite
	}
}

textures/des_plants/tree_leaves_back
{
	qer_editorimage textures/des_plants/tree_leaves.tga
	q3map_invert
	q3map_vertexScale 3.5
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	novlcollapse
	deformVertexes wave 16 sin 0 1 0 .2
	{
		map textures/des_plants/tree_leaves.tga
		alphaFunc GE128
		rgbGen vertex
		depthWrite
	}
}

textures/des_plants/willow_leaves
{
	qer_editorimage textures/des_plants/willow_leaves.tga
	q3map_cloneShader textures/des_plants/willow_leaves_back
	q3map_vertexscale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
	novlcollapse
	nopicmip
	deformVertexes wave 16 sin 0 1 0 .2
	{
		map textures/des_plants/willow_leaves.tga
		alphaFunc GE128
		rgbGen vertex
		depthwrite
	}
}

textures/des_plants/willow_leaves_back
{
	qer_editorimage textures/des_plants/willow_leaves.tga
	q3map_invert
	q3map_vertexScale 3.5
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	novlcollapse
	nopicmip
	deformvertexes wave 16 sin 0 1 0 .2
	{
		map textures/des_plants/willow_leaves.tga
		alphaFunc GE128
		rgbGen vertex
		depthwrite
	}
}

textures/des_plants/flower_01
{
	qer_editorimage textures/des_plants/flower_01.tga
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
   	{
		map textures/des_plants/flower_01.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/flower_01.tga
		alphaFunc GE128
		rgbGen exactvertex
		depthWrite
	}
}

textures/des_plants/flower_02
{
	qer_editorimage textures/des_plants/flower_02.tga
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
   	{
		map textures/des_plants/flower_02.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/flower_02.tga
		alphaFunc GE128
		rgbGen exactvertex
		depthWrite
	}
}

textures/des_plants/flower_03
{
	qer_editorimage textures/des_plants/flower_03.tga
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
   	{
		map textures/des_plants/flower_03.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/flower_03.tga
		alphaFunc GE128
		rgbGen exactvertex
		depthWrite
	}
}

textures/des_plants/flower_04
{
	qer_editorimage textures/des_plants/flower_04.tga
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
   	{
		map textures/des_plants/flower_04.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/flower_04.tga
		alphaFunc GE128
		rgbGen exactvertex
		depthWrite
	}
}

textures/des_plants/flower_05
{
	qer_editorimage textures/des_plants/flower_05.tga
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
   	{
		map textures/des_plants/flower_05.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/flower_05.tga
		alphaFunc GE128
		rgbGen exactvertex
		depthWrite
	}
}

textures/des_plants/flower_06
{
	qer_editorimage textures/des_plants/flower_06.tga
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
   	{
		map textures/des_plants/flower_06.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/flower_06.tga
		alphaFunc GE128
		rgbGen exactvertex
		depthWrite
	}
}

textures/des_plants/flower_07
{
	qer_editorimage textures/des_plants/flower_07.tga
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
   	{
		map textures/des_plants/flower_07.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/flower_07.tga
		alphaFunc GE128
		rgbGen exactvertex
		depthWrite
	}
}

textures/des_plants/flower_08
{
	qer_editorimage textures/des_plants/flower_08.tga
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
   	{
		map textures/des_plants/flower_08.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/flower_08.tga
		alphaFunc GE128
		rgbGen exactvertex
		depthWrite
	}
}

textures/des_plants/flower_09
{
	qer_editorimage textures/des_plants/flower_09.tga
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
   	{
		map textures/des_plants/flower_09.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/flower_09.tga
		alphaFunc GE128
		rgbGen exactvertex
		depthWrite
	}
}

textures/des_plants/flower_10
{
	qer_editorimage textures/des_plants/flower_10.tga
	q3map_vertexScale 1.25
	surfaceparm trans
	surfaceparm nonsolid
	surfaceparm nomarks
	surfaceparm nolightmap
	surfaceparm alphashadow
	qer_trans 0.99
   	{
		map textures/des_plants/flower_10.tga
		blendFunc GL_SRC_ALPHA GL_ONE_MINUS_SRC_ALPHA
		rgbGen vertex
	}
	{
		map textures/des_plants/flower_10.tga
		alphaFunc GE128
		rgbGen exactvertex
		depthWrite
	}
}