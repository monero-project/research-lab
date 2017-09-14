package how.monero.hodl.util;

public class ExceptionAdapter {
  public static RuntimeException toRuntimeException(Exception e) {
    if(RuntimeException.class.isInstance(e)) return (RuntimeException) e;
    else return new RuntimeException(e);
  }
}
