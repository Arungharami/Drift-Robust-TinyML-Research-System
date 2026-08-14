from pathlib import Path
import numpy as np
from src.data.loader import load_batch
def test_sparse_loader(tmp_path: Path):
    p=tmp_path/"batch1.dat"; p.write_text("1 1:2.5 128:-1\n")
    x,y=load_batch(p); assert x.shape==(1,128); assert np.allclose(x[0,[0,127]],[2.5,-1]); assert y.tolist()==[1]
