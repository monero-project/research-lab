#the goal with this is to automagically Convert MiniNero Code to ref10 C equivalent
import MiniNero

def t_header():
    print("#include <stdlib.h>")
    print("#include <stdio.h>")
    print("#include <string.h>")
    print("#include <stdint.h>")
    print("#include \"crypto-ops.h\"")
    print("#include \"crypto.h\"\n\n")
    print("#include \"keccak.h\"")
    print("#define BYTES 64\n\n")
    print("int main(int argc, char *argv[]) {\n\n")

def t_footer():
    print("return 0;\n}\n\n")

def hexToC(key):
    while len(key) < 64:
        key = key + "0"
    k2 = [key[i:i+2] for i in range(0, len(key), 2)]
    ar = "{{0x"+(", 0x".join(k2))+"}}"
    print(ar)
    
def sigToC(r, c):
    r2 = [r[i:i+2] for i in range(0, len(r), 2)]
    ar = "{0x"+(", 0x".join(r2))+"}"
    c2 = [c[i:i+2] for i in range(0, len(c), 2)]
    ac = "{0x"+(", 0x".join(c2))+"}"
    print("signature sig  = {"+ac+", "+ar+"};\n\n")


def t_scalarmultBase(name_in, name_out):
    print("//Running scalarmult Base on "+name_in)
    print("ge_p3 point;")
    print("ge_scalarmult_base(&point, "+name_in+");")
    print("unsigned char "+name_out+"[32];")
    print("ge_p3_tobytes("+name_out+", &point);\n\n")

def t_cn_fast_hash(name_in, name_out):
        print("\n//running cn_fast_hash on "+name_in)
        print("uint8_t md2[32];")
        print("unsigned char "+name_out+"[32] = {0};")
        print("int j = 0;")
        print("keccak((uint8_t *) "+name_in+", 32, md2, 32);")
        print("for (j= 0 ; j < 32 ; j++) {")
        print("h[j] = (unsigned char)md2[j];")
        print("}")
        print("printf(\"\\nhash:\\n\");")
        print("for (j = 0 ; j < 32 ; j++) {")
        print("printf(\"%02x\", "+name_out+"[j]);")
        print("}")


