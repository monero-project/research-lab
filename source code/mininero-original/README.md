# MiniNero

Copyright (c) 2014, The Monero Project

## About this Project

MiniNero is a reimplementation of CryptoNote one-time ring signatures in Python, and is roughly analogous with the way they are implemented in Monero. The main source that was used for creating MiniNero are the functions contained in crypto.cpp and crypto-ops.cpp in Monero. MiniNero produces working and valid ring signatures, although they differ slightly from the Monero ring signatures due to hashing and packing differences between the libraries used.

## License

Copyright (c) 2014, The Monero Project

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Parts of the project are originally copyright (c) 2012-2013 The Cryptonote developers

## Using MiniNero

Dependencies: Python 2.7+, PyCrypto 2.6+

Usage: ```python mininero.py <command>```

The following commands are available:

* rs - demos MiniNero the random_scalar function
* keys - demos MiniNero key generation
* fasthash - demos MiniNero fast hash 
* hashscalar - demos MiniNero H_s(P) equivalent function 
* hashcurve - demos MiniNero H_p(P)
* checkkey - demos MiniNero check_key function
* secpub - demos turning a fixed secret to a public key
* keyder - demos MiniNero Key Derivation
* dersca - demos MiniNero derivation to scalar
* derpub - demos derive public key
* dersec - demos derive secret key
* testcomm - tests the helper struct for some CN functions
* gensig - testing generate_signature
* checksig - tests checking signature
* keyimage - tests creating I=xH_p(P)
* ringsig - tests creating and checking a ringsig
* conv - tests some helper conversion functions
* red - tests some of the sc_Code
* gedb - tests some of the edwards curve functions
* sck - tests sc_check