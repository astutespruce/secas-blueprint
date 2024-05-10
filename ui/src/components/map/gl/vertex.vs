#version 300 es
#define SHADER_NAME stackedpng_vertex_shader

in vec2 texCoords;
in vec3 positions;
in vec3 positions64Low;

out vec2 vTexCoord;

uniform float coordinateConversion;

void main(void) {
  geometry.worldPosition = positions;
  geometry.uv = texCoords;
  vTexCoord = texCoords;

  gl_Position = project_position_to_clipspace(positions, positions64Low, vec3(0.), geometry.position);
}