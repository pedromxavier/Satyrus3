
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'leftADDSUBleftMULDIVleftXORORleftANDleftNOTleftIMPRIMPIFFleftEQNEGELEGTLTleftFORALLEXISTSEXISTS_ONEleftLCURRCURleftLPARRPARleftNAMEleftSTRINGNUMBERleftDOTSleftSHARPleftENDLADD AND ASSIGN COMMA DIV DOTS ENDL EQ EXISTS EXISTS_ONE FORALL GE GT IFF IMP LBRA LCUR LE LPAR LT MUL NAME NE NOT NUMBER OR RBRA RCUR RIMP RPAR SHARP STRING SUB XOR start : code\n     code : code stmt\n             | stmt\n     stmt : sys_config ENDL\n             | def_const ENDL\n             | def_array ENDL\n             | def_restr ENDL\n     sys_config : SHARP NAME DOTS NUMBER\n                   | SHARP NAME DOTS STRING\n     def_const : NAME ASSIGN literal\n     literal : NUMBER\n                | NAME\n     def_array : NAME shape ASSIGN array_buffer\n                  | NAME shape\n     shape : shape index\n              | index\n     index : LBRA literal RBRA\n     array_buffer : LCUR array RCUR\n     array : array COMMA array_item\n              | array_item\n     array_item : array_index DOTS literal\n     array_index : LPAR literal_seq RPAR\n     literal_seq : literal_seq COMMA literal\n                    | literal\n     def_restr : LPAR NAME RPAR NAME RBRA literal RBRA DOTS loops expr\n                  | LPAR NAME RPAR NAME DOTS loops expr\n     loops : loops loop\n              | loop\n     loop : quant LCUR NAME ASSIGN domain COMMA conditions RCUR\n             | quant LCUR NAME ASSIGN domain RCUR\n     quant : FORALL\n              | EXISTS\n              | EXISTS_ONE\n     domain : LBRA literal DOTS literal DOTS literal RBRA\n               | LBRA literal DOTS literal RBRA\n     conditions : conditions COMMA condition\n                   | condition\n     condition : expr EQ expr\n                  | expr GT expr\n                  | expr LT expr\n                  | expr GE expr\n                  | expr LE expr\n                  | expr NE expr\n     condition : expr\n     expr : literal\n     expr : NOT expr\n             | ADD expr\n             | SUB expr\n     expr : expr AND expr\n             | expr OR expr\n             | expr XOR expr\n             | expr ADD expr\n             | expr SUB expr\n             | expr MUL expr\n             | expr DIV expr\n             | expr IMP expr\n             | expr RIMP expr\n             | expr IFF expr\n     expr : expr LBRA expr RBRA\n     expr : LPAR expr RPAR\n    '
    
_lr_action_items = {'SHARP':([0,2,3,11,12,13,14,15,],[8,8,-3,-2,-4,-5,-6,-7,]),'NAME':([0,2,3,8,10,11,12,13,14,15,17,20,29,39,40,44,48,49,57,59,61,63,64,65,66,70,71,72,73,74,75,76,77,78,79,80,85,102,103,104,109,110,111,112,113,114,115,116,117,126,],[9,9,-3,16,21,-2,-4,-5,-6,-7,23,23,35,23,23,23,23,-28,23,23,-27,23,23,23,84,23,23,23,23,23,23,23,23,23,23,23,23,23,23,-30,23,23,-29,23,23,23,23,23,23,23,]),'LPAR':([0,2,3,11,12,13,14,15,33,43,48,49,59,61,63,64,65,70,71,72,73,74,75,76,77,78,79,80,85,103,104,110,111,112,113,114,115,116,117,],[10,10,-3,-2,-4,-5,-6,-7,39,39,59,-28,59,-27,59,59,59,59,59,59,59,59,59,59,59,59,59,59,59,59,-30,59,-29,59,59,59,59,59,59,]),'$end':([1,2,3,11,12,13,14,15,],[0,-1,-3,-2,-4,-5,-6,-7,]),'ENDL':([4,5,6,7,18,19,23,24,25,27,30,31,32,34,42,60,62,81,82,83,86,87,88,89,90,91,92,93,94,95,96,99,100,],[12,13,14,15,-14,-16,-12,-10,-11,-15,-8,-9,-13,-17,-18,-26,-45,-46,-47,-48,-60,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,-25,-59,]),'ASSIGN':([9,18,19,27,34,84,],[17,26,-16,-15,-17,98,]),'LBRA':([9,18,19,23,25,27,34,60,62,69,81,82,83,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,108,120,121,122,123,124,125,],[20,20,-16,-12,-11,-15,-17,80,-45,80,-46,-47,-48,-60,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,80,102,80,-59,80,80,80,80,80,80,80,]),'DOTS':([16,23,25,35,38,56,58,105,118,],[22,-12,-11,41,44,-22,68,109,126,]),'NUMBER':([17,20,22,39,40,44,48,49,57,59,61,63,64,65,70,71,72,73,74,75,76,77,78,79,80,85,102,103,104,109,110,111,112,113,114,115,116,117,126,],[25,25,30,25,25,25,25,-28,25,25,-27,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,-30,25,25,-29,25,25,25,25,25,25,25,]),'RPAR':([21,23,25,45,46,62,67,69,81,82,83,86,87,88,89,90,91,92,93,94,95,96,100,],[29,-12,-11,56,-24,-45,-23,86,-46,-47,-48,-60,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,-59,]),'STRING':([22,],[31,]),'RBRA':([23,25,28,35,47,62,81,82,83,86,87,88,89,90,91,92,93,94,95,96,97,100,118,128,],[-12,-11,34,40,58,-45,-46,-47,-48,-60,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,100,-59,127,129,]),'COMMA':([23,25,36,37,45,46,54,55,62,67,81,82,83,86,87,88,89,90,91,92,93,94,95,96,100,101,106,107,108,119,120,121,122,123,124,125,127,129,],[-12,-11,43,-20,57,-24,-19,-21,-45,-23,-46,-47,-48,-60,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,-59,103,110,-37,-44,-36,-38,-39,-40,-41,-42,-43,-35,-34,]),'RCUR':([23,25,36,37,54,55,62,81,82,83,86,87,88,89,90,91,92,93,94,95,96,100,101,106,107,108,119,120,121,122,123,124,125,127,129,],[-12,-11,42,-20,-19,-21,-45,-46,-47,-48,-60,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,-59,104,111,-37,-44,-36,-38,-39,-40,-41,-42,-43,-35,-34,]),'AND':([23,25,60,62,69,81,82,83,86,87,88,89,90,91,92,93,94,95,96,97,99,100,108,120,121,122,123,124,125,],[-12,-11,70,-45,70,-46,70,70,-60,-49,70,70,70,70,70,70,-56,-57,-58,70,70,-59,70,70,70,70,70,70,70,]),'OR':([23,25,60,62,69,81,82,83,86,87,88,89,90,91,92,93,94,95,96,97,99,100,108,120,121,122,123,124,125,],[-12,-11,71,-45,71,-46,71,71,-60,-49,-50,-51,71,71,71,71,-56,-57,-58,71,71,-59,71,71,71,71,71,71,71,]),'XOR':([23,25,60,62,69,81,82,83,86,87,88,89,90,91,92,93,94,95,96,97,99,100,108,120,121,122,123,124,125,],[-12,-11,72,-45,72,-46,72,72,-60,-49,-50,-51,72,72,72,72,-56,-57,-58,72,72,-59,72,72,72,72,72,72,72,]),'ADD':([23,25,48,49,59,60,61,62,63,64,65,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,85,86,87,88,89,90,91,92,93,94,95,96,97,99,100,103,104,108,110,111,112,113,114,115,116,117,120,121,122,123,124,125,],[-12,-11,64,-28,64,73,-27,-45,64,64,64,73,64,64,64,64,64,64,64,64,64,64,64,-46,-47,-48,64,-60,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,73,73,-59,64,-30,73,64,-29,64,64,64,64,64,64,73,73,73,73,73,73,]),'SUB':([23,25,48,49,59,60,61,62,63,64,65,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,85,86,87,88,89,90,91,92,93,94,95,96,97,99,100,103,104,108,110,111,112,113,114,115,116,117,120,121,122,123,124,125,],[-12,-11,65,-28,65,74,-27,-45,65,65,65,74,65,65,65,65,65,65,65,65,65,65,65,-46,-47,-48,65,-60,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,74,74,-59,65,-30,74,65,-29,65,65,65,65,65,65,74,74,74,74,74,74,]),'MUL':([23,25,60,62,69,81,82,83,86,87,88,89,90,91,92,93,94,95,96,97,99,100,108,120,121,122,123,124,125,],[-12,-11,75,-45,75,-46,75,75,-60,-49,-50,-51,75,75,-54,-55,-56,-57,-58,75,75,-59,75,75,75,75,75,75,75,]),'DIV':([23,25,60,62,69,81,82,83,86,87,88,89,90,91,92,93,94,95,96,97,99,100,108,120,121,122,123,124,125,],[-12,-11,76,-45,76,-46,76,76,-60,-49,-50,-51,76,76,-54,-55,-56,-57,-58,76,76,-59,76,76,76,76,76,76,76,]),'IMP':([23,25,60,62,69,81,82,83,86,87,88,89,90,91,92,93,94,95,96,97,99,100,108,120,121,122,123,124,125,],[-12,-11,77,-45,77,77,77,77,-60,77,77,77,77,77,77,77,-56,-57,-58,77,77,-59,77,77,77,77,77,77,77,]),'RIMP':([23,25,60,62,69,81,82,83,86,87,88,89,90,91,92,93,94,95,96,97,99,100,108,120,121,122,123,124,125,],[-12,-11,78,-45,78,78,78,78,-60,78,78,78,78,78,78,78,-56,-57,-58,78,78,-59,78,78,78,78,78,78,78,]),'IFF':([23,25,60,62,69,81,82,83,86,87,88,89,90,91,92,93,94,95,96,97,99,100,108,120,121,122,123,124,125,],[-12,-11,79,-45,79,79,79,79,-60,79,79,79,79,79,79,79,-56,-57,-58,79,79,-59,79,79,79,79,79,79,79,]),'EQ':([23,25,62,81,82,83,86,87,88,89,90,91,92,93,94,95,96,100,108,],[-12,-11,-45,-46,-47,-48,-60,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,-59,112,]),'GT':([23,25,62,81,82,83,86,87,88,89,90,91,92,93,94,95,96,100,108,],[-12,-11,-45,-46,-47,-48,-60,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,-59,113,]),'LT':([23,25,62,81,82,83,86,87,88,89,90,91,92,93,94,95,96,100,108,],[-12,-11,-45,-46,-47,-48,-60,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,-59,114,]),'GE':([23,25,62,81,82,83,86,87,88,89,90,91,92,93,94,95,96,100,108,],[-12,-11,-45,-46,-47,-48,-60,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,-59,115,]),'LE':([23,25,62,81,82,83,86,87,88,89,90,91,92,93,94,95,96,100,108,],[-12,-11,-45,-46,-47,-48,-60,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,-59,116,]),'NE':([23,25,62,81,82,83,86,87,88,89,90,91,92,93,94,95,96,100,108,],[-12,-11,-45,-46,-47,-48,-60,-49,-50,-51,-52,-53,-54,-55,-56,-57,-58,-59,117,]),'LCUR':([26,50,51,52,53,],[33,66,-31,-32,-33,]),'FORALL':([41,48,49,61,68,85,104,111,],[51,51,-28,-27,51,51,-30,-29,]),'EXISTS':([41,48,49,61,68,85,104,111,],[52,52,-28,-27,52,52,-30,-29,]),'EXISTS_ONE':([41,48,49,61,68,85,104,111,],[53,53,-28,-27,53,53,-30,-29,]),'NOT':([48,49,59,61,63,64,65,70,71,72,73,74,75,76,77,78,79,80,85,103,104,110,111,112,113,114,115,116,117,],[63,-28,63,-27,63,63,63,63,63,63,63,63,63,63,63,63,63,63,63,63,-30,63,-29,63,63,63,63,63,63,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'start':([0,],[1,]),'code':([0,],[2,]),'stmt':([0,2,],[3,11,]),'sys_config':([0,2,],[4,4,]),'def_const':([0,2,],[5,5,]),'def_array':([0,2,],[6,6,]),'def_restr':([0,2,],[7,7,]),'shape':([9,],[18,]),'index':([9,18,],[19,27,]),'literal':([17,20,39,40,44,48,57,59,63,64,65,70,71,72,73,74,75,76,77,78,79,80,85,102,103,109,110,112,113,114,115,116,117,126,],[24,28,46,47,55,62,67,62,62,62,62,62,62,62,62,62,62,62,62,62,62,62,62,105,62,118,62,62,62,62,62,62,62,128,]),'array_buffer':([26,],[32,]),'array':([33,],[36,]),'array_item':([33,43,],[37,54,]),'array_index':([33,43,],[38,38,]),'literal_seq':([39,],[45,]),'loops':([41,68,],[48,85,]),'loop':([41,48,68,85,],[49,61,49,61,]),'quant':([41,48,68,85,],[50,50,50,50,]),'expr':([48,59,63,64,65,70,71,72,73,74,75,76,77,78,79,80,85,103,110,112,113,114,115,116,117,],[60,69,81,82,83,87,88,89,90,91,92,93,94,95,96,97,99,108,108,120,121,122,123,124,125,]),'domain':([98,],[101,]),'conditions':([103,],[106,]),'condition':([103,110,],[107,119,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> start","S'",1,None,None,None),
  ('start -> code','start',1,'p_start','sat_parser.py',35),
  ('code -> code stmt','code',2,'p_code','sat_parser.py',40),
  ('code -> stmt','code',1,'p_code','sat_parser.py',41),
  ('stmt -> sys_config ENDL','stmt',2,'p_stmt','sat_parser.py',49),
  ('stmt -> def_const ENDL','stmt',2,'p_stmt','sat_parser.py',50),
  ('stmt -> def_array ENDL','stmt',2,'p_stmt','sat_parser.py',51),
  ('stmt -> def_restr ENDL','stmt',2,'p_stmt','sat_parser.py',52),
  ('sys_config -> SHARP NAME DOTS NUMBER','sys_config',4,'p_sys_config','sat_parser.py',57),
  ('sys_config -> SHARP NAME DOTS STRING','sys_config',4,'p_sys_config','sat_parser.py',58),
  ('def_const -> NAME ASSIGN literal','def_const',3,'p_def_const','sat_parser.py',64),
  ('literal -> NUMBER','literal',1,'p_literal','sat_parser.py',70),
  ('literal -> NAME','literal',1,'p_literal','sat_parser.py',71),
  ('def_array -> NAME shape ASSIGN array_buffer','def_array',4,'p_def_array','sat_parser.py',76),
  ('def_array -> NAME shape','def_array',2,'p_def_array','sat_parser.py',77),
  ('shape -> shape index','shape',2,'p_shape','sat_parser.py',88),
  ('shape -> index','shape',1,'p_shape','sat_parser.py',89),
  ('index -> LBRA literal RBRA','index',3,'p_index','sat_parser.py',97),
  ('array_buffer -> LCUR array RCUR','array_buffer',3,'p_array_buffer','sat_parser.py',102),
  ('array -> array COMMA array_item','array',3,'p_array','sat_parser.py',107),
  ('array -> array_item','array',1,'p_array','sat_parser.py',108),
  ('array_item -> array_index DOTS literal','array_item',3,'p_array_item','sat_parser.py',116),
  ('array_index -> LPAR literal_seq RPAR','array_index',3,'p_array_index','sat_parser.py',121),
  ('literal_seq -> literal_seq COMMA literal','literal_seq',3,'p_literal_seq','sat_parser.py',126),
  ('literal_seq -> literal','literal_seq',1,'p_literal_seq','sat_parser.py',127),
  ('def_restr -> LPAR NAME RPAR NAME RBRA literal RBRA DOTS loops expr','def_restr',10,'p_def_restr','sat_parser.py',135),
  ('def_restr -> LPAR NAME RPAR NAME DOTS loops expr','def_restr',7,'p_def_restr','sat_parser.py',136),
  ('loops -> loops loop','loops',2,'p_loops','sat_parser.py',153),
  ('loops -> loop','loops',1,'p_loops','sat_parser.py',154),
  ('loop -> quant LCUR NAME ASSIGN domain COMMA conditions RCUR','loop',8,'p_loop','sat_parser.py',162),
  ('loop -> quant LCUR NAME ASSIGN domain RCUR','loop',6,'p_loop','sat_parser.py',163),
  ('quant -> FORALL','quant',1,'p_quant','sat_parser.py',171),
  ('quant -> EXISTS','quant',1,'p_quant','sat_parser.py',172),
  ('quant -> EXISTS_ONE','quant',1,'p_quant','sat_parser.py',173),
  ('domain -> LBRA literal DOTS literal DOTS literal RBRA','domain',7,'p_domain','sat_parser.py',178),
  ('domain -> LBRA literal DOTS literal RBRA','domain',5,'p_domain','sat_parser.py',179),
  ('conditions -> conditions COMMA condition','conditions',3,'p_conditions','sat_parser.py',187),
  ('conditions -> condition','conditions',1,'p_conditions','sat_parser.py',188),
  ('condition -> expr EQ expr','condition',3,'p_condition','sat_parser.py',196),
  ('condition -> expr GT expr','condition',3,'p_condition','sat_parser.py',197),
  ('condition -> expr LT expr','condition',3,'p_condition','sat_parser.py',198),
  ('condition -> expr GE expr','condition',3,'p_condition','sat_parser.py',199),
  ('condition -> expr LE expr','condition',3,'p_condition','sat_parser.py',200),
  ('condition -> expr NE expr','condition',3,'p_condition','sat_parser.py',201),
  ('condition -> expr','condition',1,'p_condition_expr','sat_parser.py',206),
  ('expr -> literal','expr',1,'p_expr','sat_parser.py',211),
  ('expr -> NOT expr','expr',2,'p_expr1','sat_parser.py',216),
  ('expr -> ADD expr','expr',2,'p_expr1','sat_parser.py',217),
  ('expr -> SUB expr','expr',2,'p_expr1','sat_parser.py',218),
  ('expr -> expr AND expr','expr',3,'p_expr2','sat_parser.py',223),
  ('expr -> expr OR expr','expr',3,'p_expr2','sat_parser.py',224),
  ('expr -> expr XOR expr','expr',3,'p_expr2','sat_parser.py',225),
  ('expr -> expr ADD expr','expr',3,'p_expr2','sat_parser.py',226),
  ('expr -> expr SUB expr','expr',3,'p_expr2','sat_parser.py',227),
  ('expr -> expr MUL expr','expr',3,'p_expr2','sat_parser.py',228),
  ('expr -> expr DIV expr','expr',3,'p_expr2','sat_parser.py',229),
  ('expr -> expr IMP expr','expr',3,'p_expr2','sat_parser.py',230),
  ('expr -> expr RIMP expr','expr',3,'p_expr2','sat_parser.py',231),
  ('expr -> expr IFF expr','expr',3,'p_expr2','sat_parser.py',232),
  ('expr -> expr LBRA expr RBRA','expr',4,'p_expr_index','sat_parser.py',237),
  ('expr -> LPAR expr RPAR','expr',3,'p_expr_par','sat_parser.py',242),
]
