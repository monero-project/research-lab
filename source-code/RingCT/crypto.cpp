#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <mutex>

#include "varint.h"
#include "warnings.h"
#include "crypto.h"
#include "keccak.h"
#include "hash-ops.h"
#include "generic-ops.h"



#include <stdlib.h>




namespace crypto {

  using std::abort;
  using std::int32_t;
  using std::int64_t;
  using std::lock_guard;
  using std::mutex;
  using std::size_t;
  using std::uint32_t;
  using std::uint64_t;

  extern "C" {
#include "crypto-ops.h"
#include "random.h"
  }



  mutex random_lock;




  static inline unsigned char *operator &(ec_point &point) {
    return &reinterpret_cast<unsigned char &>(point);
  }

  static inline const unsigned char *operator &(const ec_point &point) {
    return &reinterpret_cast<const unsigned char &>(point);
  }

  static inline unsigned char *operator &(ec_scalar &scalar) {
    return &reinterpret_cast<unsigned char &>(scalar);
  }

  static inline const unsigned char *operator &(const ec_scalar &scalar) {
    return &reinterpret_cast<const unsigned char &>(scalar);
  }

  /* generate a random 32-byte (256-bit) integer and copy it to res */
  static inline void random_scalar(ec_scalar &res) {
    unsigned char tmp[64];
    generate_random_bytes(64, tmp);
    sc_reduce(tmp);
    memcpy(&res, tmp, 32);
  }

  static void hash_to_scalar(const void *data, size_t length, ec_scalar &res) { //was static inline void
    cn_fast_hashh(data, length, reinterpret_cast<hash &>(res)); //this is the void one.. reinterp is trying to get it  from ec_scalar to the correct thing...

    sc_reduce32(&res);
  }

  /* 
   * generate public and secret keys from a random 256-bit integer
   * TODO: allow specifiying random value (for wallet recovery)
   * 
   */
  secret_key crypto_ops::generate_keys(public_key &pub, secret_key &sec, const secret_key& recovery_key, bool recover) {
    lock_guard<mutex> lock(random_lock);
    ge_p3 point;

    secret_key rng;

    if (recover)
    {
      rng = recovery_key;
    }
    else
    {
      random_scalar(rng);
    }
    sec = rng;
    sc_reduce32(&sec);  // reduce in case second round of keys (sendkeys)

    ge_scalarmult_base(&point, &sec);
    ge_p3_tobytes(&pub, &point);

    return rng;
  }

  bool crypto_ops::check_key(const public_key &key) {
    ge_p3 point;
    return ge_frombytes_vartime(&point, &key) == 0;
  }

  bool crypto_ops::secret_key_to_public_key(const secret_key &sec, public_key &pub) {
    ge_p3 point;
    if (sc_check(&sec) != 0) {
      return false;
    }
    ge_scalarmult_base(&point, &sec);
    ge_p3_tobytes(&pub, &point);
    return true;
  }

  bool crypto_ops::generate_key_derivation(const public_key &key1, const secret_key &key2, key_derivation &derivation) {
    ge_p3 point;
    ge_p2 point2;
    ge_p1p1 point3;
    assert(sc_check(&key2) == 0);
    if (ge_frombytes_vartime(&point, &key1) != 0) {
      return false;
    }
    ge_scalarmult(&point2, &key2, &point);
    ge_mul8(&point3, &point2);
    ge_p1p1_to_p2(&point2, &point3);
    ge_tobytes(&derivation, &point2);
    return true;
  }

  static void derivation_to_scalar(const key_derivation &derivation, size_t output_index, ec_scalar &res) {
    struct {
      key_derivation derivation;
      char output_index[(sizeof(size_t) * 8 + 6) / 7];
    } buf;
    char *end = buf.output_index;
    buf.derivation = derivation;
    tools::write_varint(end, output_index);
    assert(end <= buf.output_index + sizeof buf.output_index);
    hash_to_scalar(&buf, end - reinterpret_cast<char *>(&buf), res);
  }

  bool crypto_ops::derive_public_key(const key_derivation &derivation, size_t output_index,
    const public_key &base, public_key &derived_key) {
    ec_scalar scalar;
    ge_p3 point1;
    ge_p3 point2;
    ge_cached point3;
    ge_p1p1 point4;
    ge_p2 point5;
    if (ge_frombytes_vartime(&point1, &base) != 0) {
      return false;
    }
    derivation_to_scalar(derivation, output_index, scalar);
    ge_scalarmult_base(&point2, &scalar);
    ge_p3_to_cached(&point3, &point2);
    ge_add(&point4, &point1, &point3);
    ge_p1p1_to_p2(&point5, &point4);
    ge_tobytes(&derived_key, &point5);
    return true;
  }

  void crypto_ops::derive_secret_key(const key_derivation &derivation, size_t output_index,
    const secret_key &base, secret_key &derived_key) {
    ec_scalar scalar;
    assert(sc_check(&base) == 0);
    derivation_to_scalar(derivation, output_index, scalar);
    sc_add(&derived_key, &base, &scalar);
  }

  struct s_comm {
    hash h;
    ec_point key;
    ec_point comm;
  };

  void crypto_ops::generate_signature(const hash &prefix_hash, const public_key &pub, const secret_key &sec, signature &sig) {
    lock_guard<mutex> lock(random_lock);
    ge_p3 tmp3;
    ec_scalar k;
    //ec_scalar k = {{0xbf, 0x4b, 0xa0, 0xc8, 0x81, 0xda, 0x40, 0xc9, 0x89, 0x29, 0x27, 0x75, 0x43, 0xe7, 0x38, 0x25, 0xb8, 0xcc, 0x5a, 0x73, 0x21, 0x8a, 0x12, 0x65, 0xa0, 0xf8, 0x33, 0x37, 0x60, 0x17, 0x92, 0x06}}; //uncomment for testing purposes

    s_comm buf;
#if !defined(NDEBUG)
    {
      ge_p3 t;
      public_key t2;
      assert(sc_check(&sec) == 0);
      ge_scalarmult_base(&t, &sec);
      ge_p3_tobytes(&t2, &t);
      assert(pub == t2);
    }
#endif
    buf.h = prefix_hash;
    buf.key = pub;
    random_scalar(k); //fix a scalar k for testing purposes
    
    ge_scalarmult_base(&tmp3, &k);
    ge_p3_tobytes(&buf.comm, &tmp3);
    //printv(buf.comm.data, "comm"); //testing
    hash_to_scalar(&buf, sizeof(s_comm), sig.c);
    //printf("here2\n");
    sc_mulsub(&sig.r, &sig.c, &sec, &k); //k - c*sec mod l
  }

  bool crypto_ops::check_signature(const hash &prefix_hash, const public_key &pub, const signature &sig) {
    ge_p2 tmp2;
    ge_p3 tmp3;
    ec_scalar c;
    s_comm buf;
    assert(check_key(pub));
    buf.h = prefix_hash;
    buf.key = pub;
    if (ge_frombytes_vartime(&tmp3, &pub) != 0) {
      abort();
    }
    if (sc_check(&sig.c) != 0 || sc_check(&sig.r) != 0) {
      return false;
    }
    ge_double_scalarmult_base_vartime(&tmp2, &sig.c, &tmp3, &sig.r); //tmp2 = cP + rG
    ge_tobytes(&buf.comm, &tmp2);
    hash_to_scalar(&buf, sizeof(s_comm), c);
    sc_sub(&c, &c, &sig.c);
    return sc_isnonzero(&c) == 0;
  }

  static void hash_to_ec(const public_key &key, ge_p3 &res) {
    hash h;
    ge_p2 point;
    ge_p1p1 point2;
    cn_fast_hashh(std::addressof(key), sizeof(public_key), h);
    ge_fromfe_frombytes_vartime(&point, reinterpret_cast<const unsigned char *>(&h));
    ge_mul8(&point2, &point);
    ge_p1p1_to_p3(&res, &point2);
  }

  void crypto_ops::generate_key_image(const public_key &pub, const secret_key &sec, key_image &image) {
    ge_p3 point;
    ge_p2 point2;
    assert(sc_check(&sec) == 0);
    hash_to_ec(pub, point);
    ge_scalarmult(&point2, &sec, &point);
    ge_tobytes(&image, &point2);
  }

  struct rs_comm {
    hash h;
    struct {
      ec_point a, b;
    } ab[];
  };

  static inline size_t rs_comm_size(size_t pubs_count) {
    return sizeof(rs_comm) + pubs_count * sizeof(rs_comm().ab[0]);
  }

  void crypto_ops::generate_ring_signature(const hash &prefix_hash, const key_image &image,
    const public_key *const *pubs, size_t pubs_count,
    const secret_key &sec, size_t sec_index,
    signature *sig) {
    lock_guard<mutex> lock(random_lock);
    size_t i;
    ge_p3 image_unp;
    ge_dsmp image_pre;
    ec_scalar sum, k, h;
    rs_comm *const buf = reinterpret_cast<rs_comm *>(alloca(rs_comm_size(pubs_count)));
    assert(sec_index < pubs_count);
#if !defined(NDEBUG)
    {
      ge_p3 t;
      public_key t2;
      key_image t3;
      assert(sc_check(&sec) == 0);
      ge_scalarmult_base(&t, &sec);
      ge_p3_tobytes(&t2, &t);
      assert(*pubs[sec_index] == t2);
      generate_key_image(*pubs[sec_index], sec, t3);
      assert(image == t3);
      for (i = 0; i < pubs_count; i++) {
        assert(check_key(*pubs[i]));
      }
    }
#endif
    if (ge_frombytes_vartime(&image_unp, &image) != 0) {
      abort();
    }
    ge_dsm_precomp(image_pre, &image_unp);
    sc_0(&sum);
    buf->h = prefix_hash;
    for (i = 0; i < pubs_count; i++) {
      ge_p2 tmp2;
      ge_p3 tmp3;
      if (i == sec_index) {
        random_scalar(k);
        ge_scalarmult_base(&tmp3, &k);
        ge_p3_tobytes(&buf->ab[i].a, &tmp3);
        hash_to_ec(*pubs[i], tmp3);
        ge_scalarmult(&tmp2, &k, &tmp3);
        ge_tobytes(&buf->ab[i].b, &tmp2);
      } else {
        random_scalar(sig[i].c);
        random_scalar(sig[i].r);
        if (ge_frombytes_vartime(&tmp3, &*pubs[i]) != 0) {
          abort();
        }
        ge_double_scalarmult_base_vartime(&tmp2, &sig[i].c, &tmp3, &sig[i].r);
        ge_tobytes(&buf->ab[i].a, &tmp2);
        hash_to_ec(*pubs[i], tmp3);
        ge_double_scalarmult_precomp_vartime(&tmp2, &sig[i].r, &tmp3, &sig[i].c, image_pre);
        ge_tobytes(&buf->ab[i].b, &tmp2);
        sc_add(&sum, &sum, &sig[i].c);
      }
    }
    hash_to_scalar(buf, rs_comm_size(pubs_count), h);
    sc_sub(&sig[sec_index].c, &h, &sum);
    sc_mulsub(&sig[sec_index].r, &sig[sec_index].c, &sec, &k);
  }

  bool crypto_ops::check_ring_signature(const hash &prefix_hash, const key_image &image,
    const public_key *const *pubs, size_t pubs_count,
    const signature *sig) {
    size_t i;
    ge_p3 image_unp;
    ge_dsmp image_pre;
    ec_scalar sum, h;
    rs_comm *const buf = reinterpret_cast<rs_comm *>(alloca(rs_comm_size(pubs_count)));
#if !defined(NDEBUG)
    for (i = 0; i < pubs_count; i++) {
      assert(check_key(*pubs[i]));
    }
#endif
    if (ge_frombytes_vartime(&image_unp, &image) != 0) {
      return false;
    }
    ge_dsm_precomp(image_pre, &image_unp);
    sc_0(&sum);
    buf->h = prefix_hash;
    for (i = 0; i < pubs_count; i++) {
      ge_p2 tmp2;
      ge_p3 tmp3;
      if (sc_check(&sig[i].c) != 0 || sc_check(&sig[i].r) != 0) {
        return false;
      }
      if (ge_frombytes_vartime(&tmp3, &*pubs[i]) != 0) {
        abort();
      }
      ge_double_scalarmult_base_vartime(&tmp2, &sig[i].c, &tmp3, &sig[i].r);
      ge_tobytes(&buf->ab[i].a, &tmp2);
      hash_to_ec(*pubs[i], tmp3);
      ge_double_scalarmult_precomp_vartime(&tmp2, &sig[i].r, &tmp3, &sig[i].c, image_pre);
      ge_tobytes(&buf->ab[i].b, &tmp2);
      sc_add(&sum, &sum, &sig[i].c);
    }
    hash_to_scalar(buf, rs_comm_size(pubs_count), h);
    sc_sub(&h, &h, &sum);
    return sc_isnonzero(&h) == 0;
  }
}

CRYPTO_MAKE_HASHABLE(hash) //these are in generic-ops.h
CRYPTO_MAKE_COMPARABLE(hash8)
