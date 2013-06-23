package water.fvec;

import water.*;

// The empty-compression function, where data is in 'int's.
public class C4FChunk extends Chunk {
  C4FChunk( byte[] bs ) { _mem=bs; _start = -1; _len = _mem.length>>2; }
  @Override protected final long at8_impl( int i ) {
    float res = UDP.get4f(_mem,i<<2);
    return Float.isNaN(res)?_vec._iNA:(long)res;
  }
  @Override protected final double atd_impl( int i ) {
    float res = UDP.get4f(_mem,i<<2);
    return Float.isNaN(res)?_vec._fNA:res;
  }
  @Override void   append2 ( long l, int exp ) { throw H2O.fail(); }
  @Override boolean hasFloat() { return true; }
  @Override public AutoBuffer write(AutoBuffer bb) { return bb.putA1(_mem,_mem.length); }
  @Override public C4FChunk read(AutoBuffer bb) {
    _mem = bb.bufClose();
    _start = -1;
    _len = _mem.length>>2;
    assert _mem.length == _len<<2;
    return this;
  }
}
