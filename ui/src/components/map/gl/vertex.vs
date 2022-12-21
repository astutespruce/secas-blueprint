#define SHADER_NAME stackedpng_vertex_shader

attribute vec2 texCoords;
attribute vec3 positions;
attribute vec3 positions64Low;

varying vec2 vTexCoord;

void main(void) {
  geometry.worldPosition = positions;
  geometry.uv = texCoords;
  vTexCoord = texCoords;

  gl_Position = project_position_to_clipspace(
      positions, positions64Low, vec3(0., 0., 0.), geometry.position);
}