# The prompt sync — timing the sends


Each send must follow the prompt — a too-early send lands in the
wrong read (or the input buffer before it's consumed); the recv-until
syncs the rhythm.
