"""Some pretty printing routines.
"""

def _extend_slice(source, start, end):
   """Extend the slice source[start:end] to full lines.
   Return (p0,p1,q0,q1) where source[p0:p1] is the extended slice and 
   source[p0:p1][q0:q1] == source[start:end].
   """
   p0 = source.rfind('\n', 0, start)
   if p0 == -1:
      p0 = 0
   else:
      p0 += 1
   q0 = start - p0
   p1 = source.find('\n',end-1)
   if p1 == -1:
      p1 = len(source)
   else:
      p1 += 1
   q1 = end - p0
   return (p0, p1, q0, q1)

def _extend_slice_f(source, start, end):
   """Same as _extend_slice but source is a file."""

   # XXX hack around inalid ranges in empty files
   try:
      p0 = start - 1
      while True:
         if p0 < 0:
            break
         source.seek(p0)
         c = source.read(1)
         if c == '\n':
            break
         p0 -= 1
      p0 += 1
      q0 = start - p0
      p1 = end - 1
      source.seek(p1)
      while True:
         c = source.read(1)
         if c == '' or c == '\n':
            break
      p1 = source.tell()
      q1 = end - p0
      return (p0,p1,q0,q1)
   except IOError:
      return (0,0,0,0)

def _underline_slice(source, start, end):
   # XXX TODO if the slice is a point (ie start = end) it would make more sense
   # to point it out using '^' rather than '||'
   
   tabwidth = 8
   ul = '-'
   result = ''
   tabpos = 0
   for i, c in enumerate(source):
      if start == i:
         if c == '\n':
            d = '|' + '\n'
         elif c == '\t':
            d = '|' + ul * (tabwidth-tabpos-1)
         else:
            d = '|'
      elif i == end-1:
         if c == '\n':
            d = '|' + '\n'
         elif c == '\t':
            d = ul * (tabwidth-tabpos-1) + '|'
         else:
            d = '|'
      elif start < i < end-1:
         if c == '\n':
            d = ul + '\n'
         elif c == '\t':
            d = ul * (tabwidth-tabpos)
         else:
            d = ul
      else:
         if c == '\n':
            d = '\n'
         elif c == '\t':
            d = ' ' * (tabwidth-tabpos)
         else:
            d = ' '
      result += d
      if c == '\n':
         tabpos = 0
      else:
         tabpos = (tabpos + 1) % tabwidth
   return result


# XXX much of this and pp_slice_f is duplicate and can be merged using StringIO.
# XXX TODO: sliceses should be ellipsized when they are beoynd 2 lines.

def pp_slice(source, start, end):
   """Return the slice source[start:end] extended to full lines with
   source[start:end] underlined.
   Inspired by ``An LR Substring Parse for Noncorrection Syntax Error Recovery'', Gordon V. Cormack.
   """
   (p0, p1, q0, q1) = _extend_slice(source, start, end)
   s = source[p0:p1]
   t = _underline_slice(s, q0, q1)
   l0 = source.count('\n', 0, p0) + 1
   s = s.splitlines()
   t = t.splitlines()
   s = [str(i+l0) + '\t' + s_i for (i,s_i) in enumerate(s)]
   t = ['\t' + t_i for t_i in t]
   return '\n'.join(['\n'.join(l) for l in zip(s,t)])

def pp_slice_f(source, start, end):
   """Like pp_slice but source is a file."""
   (p0,p1,q0,q1) = _extend_slice_f(source,start,end)
   source.seek(p0)
   s = source.read(p1-p0)
   t = _underline_slice(s,q0,q1)
   l0 = 1
   source.seek(0)
   while True:
      if source.tell() == p0:
         break
      c = source.read(1)
      if c == '\n':
         l0 += 1
   s = s.splitlines()
   t = t.splitlines()
   s = [str(i+l0) + '\t' + s_i for (i,s_i) in enumerate(s)]
   t = ['\t' + t_i for t_i in t]
   return '\n'.join(['\n'.join(l) for l in zip(s,t)])
