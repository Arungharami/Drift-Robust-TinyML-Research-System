from src.utils.hashing import stable_hash
def test_stable_hash_ignores_mapping_order(): assert stable_hash({"a":1,"b":2}) == stable_hash({"b":2,"a":1})
