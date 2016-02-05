#pragma once

#include <stddef.h>
#include "hash-ops.h" //needed for hash_permutation
#include "keccak.h"

void generate_random_bytes(size_t n, void *result);
inline void hash_permutation(union hash_state *state) {
  keccakf((uint64_t*)state, 24);
} //brought over from hash.h

