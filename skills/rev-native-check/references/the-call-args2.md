# The call's args — at the call site


At `call strcmp`: rdi and rsi hold the two operands — at the call
site they're set; at the entry they're live — read them either place.
