# RTP — audio inside a capture

Audio in a pcap: rtp_extract.py lists RTP streams by SSRC and
decodes PCMU/PCMA to a WAV — the output feeds dtmf_decode.

## The call

    python3 tools/forensics/rtp_extract.py call.pcap
    python3 tools/forensics/rtp_extract.py call.pcap --ssrc 0xNNN --out call.wav
