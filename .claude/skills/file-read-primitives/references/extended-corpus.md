# Extended Corpus — the long-tail read surfaces

## The `/sys` filesystem — the kernel-view

```
/sys/class/net/*/address          — MACs
/sys/class/net/*/mtu              — MTUs
/sys/class/net/*/speed            — link-speed
/sys/class/net/*/duplex           — duplex
/sys/class/net/*/operstate        — up/down
/sys/class/net/*/flags            — iface-flags
/sys/class/net/*/statistics/*
/sys/class/net/*/device/*
/sys/class/net/*/subsystem/*
/sys/class/net/*/uevent
/sys/class/net/*/ifindex
/sys/class/net/*/iflink
/sys/class/net/*/type
/sys/class/net/*/link_mode
/sys/class/net/*/carrier
/sys/class/net/*/carrier_changes
/sys/class/net/*/carrier_up_count
/sys/class/net/*/carrier_down_count
/sys/class/net/*/speed
/sys/class/net/*/duplex
/sys/class/net/*/port_id
/sys/class/net/*/port_instance_id
/sys/class/net/*/proto_down
/sys/class/net/*/dormant
/sys/class/net/*/testing
/sys/class/net/*/parentdev
/sys/class/net/*/dev_id
/sys/class/net/*/dev_port
/sys/class/net/*/devlink_port
/sys/class/net/*/addr_assign_type
/sys/class/net/*/addr_len
/sys/class/net/*/broadcast
/sys/class/net/*/ifalias
/sys/class/net/*/ifindex
/sys/class/net/*/iflink
/sys/class/net/*/name_assign_type
/sys/class/net/*/group
/sys/class/net/*/power/*
/sys/class/net/*/power/control
/sys/class/net/*/power/runtime_active_time
/sys/class/net/*/power/runtime_active_kids
/sys/class/net/*/power/runtime_enabled
/sys/class/net/*/power/runtime_status
/sys/class/net/*/power/runtime_suspended_time
/sys/class/net/*/power/runtime_usage
/sys/class/net/*/power/async
/sys/class/net/*/power/autosuspend_delay_ms
/sys/class/net/*/power/wakeup
/sys/class/net/*/power/wakeup_abort_count
/sys/class/net/*/power/wakeup_active
/sys/class/net/*/power/wakeup_active_count
/sys/class/net/*/power/wakeup_count
/sys/class/net/*/power/wakeup_expire_count
/sys/class/net/*/power/wakeup_last_time_ms
/sys/class/net/*/power/wakeup_max_time_ms
/sys/class/net/*/power/wakeup_prevent_sleep
/sys/class/net/*/power/wakeup_source
/sys/class/net/*/power/wakeup_total_time_ms
/sys/class/net/*/power/control
/sys/class/net/*/power/runtime_active_time
/sys/class/net/*/power/runtime_active_kids
/sys/class/net/*/power/runtime_enabled
/sys/class/net/*/power/runtime_status
/sys/class/net/*/power/runtime_suspended_time
/sys/class/net/*/power/runtime_usage
/sys/class/net/*/power/async
/sys/class/net/*/power/autosuspend_delay_ms
/sys/class/net/*/power/wakeup
/sys/class/net/*/power/wakeup_abort_count
/sys/class/net/*/power/wakeup_active
/sys/class/net/*/power/wakeup_active_count
/sys/class/net/*/power/wakeup_count
/sys/class/net/*/power/wakeup_expire_count
/sys/class/net/*/power/wakeup_last_time_ms
/sys/class/net/*/power/wakeup_max_time_ms
/sys/class/net/*/power/wakeup_prevent_sleep
/sys/class/net/*/power/wakeup_source
/sys/class/net/*/power/wakeup_total_time_ms
```

`/sys/class/net/*/address` — the MACs — the net-identity leak — a
fingerprint.

## The `/sys/class/dmi` — the hardware-view

```
/sys/class/dmi/id/sys_vendor
/sys/class/dmi/id/product_name
/sys/class/dmi/id/product_version
/sys/class/dmi/id/product_serial
/sys/class/dmi/id/product_uuid
/sys/class/dmi/id/board_vendor
/sys/class/dmi/id/board_name
/sys/class/dmi/id/board_version
/sys/class/dmi/id/board_serial
/sys/class/dmi/id/board_asset_tag
/sys/class/dmi/id/chassis_vendor
/sys/class/dmi/id/chassis_type
/sys/class/dmi/id/chassis_version
/sys/class/dmi/id/chassis_serial
/sys/class/dmi/id/chassis_asset_tag
/sys/class/dmi/id/bios_vendor
/sys/class/dmi/id/bios_version
/sys/class/dmi/id/bios_date
/sys/class/dmi/id/bios_release
/sys/class/dmi/id/ec_firmware_release
/sys/class/dmi/id/modalias
/sys/class/dmi/id/uevent
/sys/class/dmi/id/power/*
```

`/sys/class/dmi/id/product_uuid`/`product_serial`/`board_serial` — the
hardware-identity — a unique-machine fingerprint.

## The `/sys/devices` — the device-tree

```
/sys/devices/system/cpu/*/online
/sys/devices/system/cpu/*/cpufreq/*
/sys/devices/system/cpu/*/topology/*
/sys/devices/system/cpu/*/cache/*
/sys/devices/system/cpu/*/power/*
/sys/devices/system/cpu/*/thermal_throttle/*
/sys/devices/system/cpu/*/microcode/*
/sys/devices/system/cpu/*/vulnerabilities/*
/sys/devices/system/cpu/smt/*
/sys/devices/system/cpu/nohz_full
/sys/devices/system/cpu/isolated
/sys/devices/system/cpu/present
/sys/devices/system/cpu/online
/sys/devices/system/cpu/offline
/sys/devices/system/cpu/possible
/sys/devices/system/cpu/kernel_max
/sys/devices/system/cpu/crash_notes
/sys/devices/system/cpu/crash_notes_size
/sys/devices/system/cpu/intel_pstate/*
/sys/devices/system/cpu/intel_pstate/status
/sys/devices/system/cpu/intel_pstate/max_perf_pct
/sys/devices/system/cpu/intel_pstate/min_perf_pct
/sys/devices/system/cpu/intel_pstate/no_turbo
/sys/devices/system/cpu/intel_pstate/num_pstates
/sys/devices/system/cpu/intel_pstate/turbo_pct
/sys/devices/system/cpu/intel_pstate/hwp_dynamic_boost
/sys/devices/system/cpu/cpufreq/*
/sys/devices/system/cpu/cpufreq/policy0/scaling_governor
/sys/devices/system/cpu/cpufreq/policy0/scaling_cur_freq
/sys/devices/system/cpu/cpufreq/policy0/scaling_min_freq
/sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq
/sys/devices/system/cpu/cpufreq/policy0/scaling_available_frequencies
/sys/devices/system/cpu/cpufreq/policy0/scaling_available_governors
/sys/devices/system/cpu/cpufreq/policy0/scaling_driver
/sys/devices/system/cpu/cpufreq/policy0/scaling_setspeed
/sys/devices/system/cpu/cpufreq/policy0/scaling_boost_frequencies
/sys/devices/system/cpu/cpufreq/policy0/scaling_boost_states
/sys/devices/system/cpu/cpufreq/policy0/cpuinfo_cur_freq
/sys/devices/system/cpu/cpufreq/policy0/cpuinfo_min_freq
/sys/devices/system/cpu/cpufreq/policy0/cpuinfo_max_freq
/sys/devices/system/cpu/cpufreq/policy0/cpuinfo_transition_latency
/sys/devices/system/cpu/cpufreq/policy0/related_cpus
/sys/devices/system/cpu/cpufreq/policy0/affected_cpus
/sys/devices/system/cpu/cpufreq/policy0/bios_limit
/sys/devices/system/cpu/cpufreq/policy0/energy_performance_preference
/sys/devices/system/cpu/cpufreq/policy0/energy_performance_available_preferences
/sys/devices/system/cpu/cpufreq/policy0/amd_pstate_highest_perf
/sys/devices/system/cpu/cpufreq/policy0/amd_pstate_max_freq
/sys/devices/system/cpu/cpufreq/policy0/amd_pstate_nominal_freq
/sys/devices/system/cpu/cpufreq/policy0/amd_pstate_lowest_nonlinear_freq
/sys/devices/system/cpu/cpufreq/policy0/amd_pstate_status
/sys/devices/system/cpu/cpufreq/policy0/amd_pstate_highest_perf
/sys/devices/system/cpu/cpufreq/policy0/amd_pstate_max_freq
/sys/devices/system/cpu/cpufreq/policy0/amd_pstate_nominal_freq
/sys/devices/system/cpu/cpufreq/policy0/amd_pstate_lowest_nonlinear_freq
/sys/devices/system/cpu/cpufreq/policy0/amd_pstate_status
/sys/devices/system/cpu/cpufreq/policy0/boost
/sys/devices/system/cpu/cpufreq/policy0/boost_frequencies
/sys/devices/system/cpu/cpufreq/policy0/boost_states
/sys/devices/system/cpu/cpufreq/boost
/sys/devices/system/cpu/cpufreq/boost_frequencies
/sys/devices/system/cpu/cpufreq/boost_states
/sys/devices/system/cpu/cpuidle/*
/sys/devices/system/cpu/cpuidle/current_driver
/sys/devices/system/cpu/cpuidle/current_governor
/sys/devices/system/cpu/cpuidle/available_governors
/sys/devices/system/cpu/cpuidle/current_driver
/sys/devices/system/cpu/cpuidle/current_governor_ro
/sys/devices/system/cpu/cpuidle/low_power_idle_cpu_residency_us
/sys/devices/system/cpu/cpuidle/low_power_idle_system_residency_us
/sys/devices/system/cpu/cpuidle/use_deepest_state
/sys/devices/system/cpu/cpuidle/available_governors
/sys/devices/system/cpu/cpuidle/current_driver
/sys/devices/system/cpu/cpuidle/current_governor
/sys/devices/system/cpu/cpuidle/current_governor_ro
/sys/devices/system/cpu/cpuidle/low_power_idle_cpu_residency_us
/sys/devices/system/cpu/cpuidle/low_power_idle_system_residency_us
/sys/devices/system/cpu/cpuidle/use_deepest_state
/sys/devices/system/cpu/vulnerabilities/*
/sys/devices/system/cpu/vulnerabilities/meltdown
/sys/devices/system/cpu/vulnerabilities/spectre_v1
/sys/devices/system/cpu/vulnerabilities/spectre_v2
/sys/devices/system/cpu/vulnerabilities/spec_store_bypass
/sys/devices/system/cpu/vulnerabilities/l1tf
/sys/devices/system/cpu/vulnerabilities/mds
/sys/devices/system/cpu/vulnerabilities/taa
/sys/devices/system/cpu/vulnerabilities/itlb_multihit
/sys/devices/system/cpu/vulnerabilities/srbds
/sys/devices/system/cpu/vulnerabilities/mmio_stale_data
/sys/devices/system/cpu/vulnerabilities/retbleed
/sys/devices/system/cpu/vulnerabilities/spec_rstack_overflow
/sys/devices/system/cpu/vulnerabilities/gds
/sys/devices/system/cpu/vulnerabilities/rfds
/sys/devices/system/cpu/vulnerabilities/bhi
/sys/devices/system/cpu/vulnerabilities/pbd
/sys/devices/system/cpu/vulnerabilities/its
/sys/devices/system/cpu/vulnerabilities/indirect_target_selection
/sys/devices/system/cpu/vulnerabilities/old_microcode
/sys/devices/system/cpu/vulnerabilities/reg_file_data_sampling
/sys/devices/system/cpu/vulnerabilities/tsx_async_abort
/sys/devices/system/cpu/vulnerabilities/itlb_multihit
/sys/devices/system/cpu/vulnerabilities/mds
/sys/devices/system/cpu/vulnerabilities/taa
/sys/devices/system/cpu/vulnerabilities/l1tf
/sys/devices/system/cpu/vulnerabilities/spec_store_bypass
/sys/devices/system/cpu/vulnerabilities/spectre_v1
/sys/devices/system/cpu/vulnerabilities/spectre_v2
/sys/devices/system/cpu/vulnerabilities/meltdown
```

`/sys/devices/system/cpu/vulnerabilities/*` — the CPU-vuln status —
`Vulnerable`/`Mitigated`/`Not affected` — a security-posture leak —
a host-fingerprint.

## The `/sys/kernel` — the kernel-view

```
/sys/kernel/debug/*                — debugfs — root usually
/sys/kernel/tracing/*              — tracefs — root usually
/sys/kernel/config/*               — configfs
/sys/kernel/mm/hugepages/*
/sys/kernel/mm/transparent_hugepage/*
/sys/kernel/mm/ksm/*
/sys/kernel/mm/swap/*
/sys/kernel/mm/page_idle/*
/sys/kernel/mm/cma/*
/sys/kernel/mm/*
/sys/kernel/power/*
/sys/kernel/power/state
/sys/kernel/power/mem_sleep
/sys/kernel/power/disk
/sys/kernel/power/image_size
/sys/kernel/power/resume
/sys/kernel/power/wakeup_count
/sys/kernel/power/pm_test
/sys/kernel/power/pm_async
/sys/kernel/power/pm_print_times
/sys/kernel/power/pm_wakeup_irq
/sys/kernel/power/pm_debug_messages
/sys/kernel/power/suspend_stats/*
/sys/kernel/power/suspend_stats/success
/sys/kernel/power/suspend_stats/fail
/sys/kernel/power/suspend_stats/failed_freeze
/sys/kernel/power/suspend_stats/failed_prepare
/sys/kernel/power/suspend_stats/failed_suspend
/sys/kernel/power/suspend_stats/failed_suspend_late
/sys/kernel/power/suspend_stats/failed_suspend_noirq
/sys/kernel/power/suspend_stats/failed_resume
/sys/kernel/power/suspend_stats/failed_resume_early
/sys/kernel/power/suspend_stats/failed_resume_noirq
/sys/kernel/power/suspend_stats/last_failed_dev
/sys/kernel/power/suspend_stats/last_failed_errno
/sys/kernel/power/suspend_stats/last_failed_step
/sys/kernel/power/pm_freeze_timeout
/sys/kernel/power/pm_test
/sys/kernel/power/pm_async
/sys/kernel/power/pm_print_times
/sys/kernel/power/pm_wakeup_irq
/sys/kernel/power/pm_debug_messages
/sys/kernel/power/pm_trace
/sys/kernel/power/pm_trace_dev_match
/sys/kernel/power/pm_debug_messages_on
/sys/kernel/power/pm_debug_messages_off
/sys/kernel/power/pm_debug_messages_level
/sys/kernel/power/pm_debug_messages_max
/sys/kernel/power/pm_debug_messages_size
/sys/kernel/power/pm_debug_messages_offset
/sys/kernel/power/pm_debug_messages_enabled
/sys/kernel/power/pm_debug_messages_disabled
/sys/kernel/power/pm_debug_messages_set
/sys/kernel/power/pm_debug_messages_get
/sys/kernel/power/pm_debug_messages_clear
/sys/kernel/power/pm_debug_messages_read
/sys/kernel/power/pm_debug_messages_write
/sys/kernel/power/pm_debug_messages_seek
/sys/kernel/power/pm_debug_messages_tell
/sys/kernel/power/pm_debug_messages_sync
/sys/kernel/power/pm_debug_messages_flush
/sys/kernel/power/pm_debug_messages_close
/sys/kernel/power/pm_debug_messages_open
/sys/kernel/power/pm_debug_messages_lock
/sys/kernel/power/pm_debug_messages_unlock
/sys/kernel/power/pm_debug_messages_wait
/sys/kernel/power/pm_debug_messages_signal
/sys/kernel/power/pm_debug_messages_poll
/sys/kernel/power/pm_debug_messages_select
/sys/kernel/power/pm_debug_messages_epoll
/sys/kernel/power/pm_debug_messages_epoll_wait
/sys/kernel/power/pm_debug_messages_epoll_ctl
/sys/kernel/power/pm_debug_messages_epoll_create
/sys/kernel/power/pm_debug_messages_epoll_create1
/sys/kernel/power/pm_debug_messages_epoll_pwait
/sys/kernel/power/pm_debug_messages_epoll_pwait2
/sys/kernel/power/pm_debug_messages_epoll_wait
/sys/kernel/power/pm_debug_messages_epoll_ctl
/sys/kernel/power/pm_debug_messages_epoll_create
/sys/kernel/power/pm_debug_messages_epoll_create1
/sys/kernel/power/pm_debug_messages_epoll_pwait
/sys/kernel/power/pm_debug_messages_epoll_pwait2
/sys/kernel/power/pm_debug_messages_epoll_wait
/sys/kernel/power/pm_debug_messages_epoll_ctl
/sys/kernel/power/pm_debug_messages_epoll_create
/sys/kernel/power/pm_debug_messages_epoll_create1
/sys/kernel/power/pm_debug_messages_epoll_pwait
/sys/kernel/power/pm_debug_messages_epoll_pwait2
```

The `/sys/kernel` tree — mostly noise, some info — `power/state` etc —
the kernel-view family — rarely needed.

## The `/sys/module` — the module-view

```
/sys/module/*/version
/sys/module/*/srcversion
/sys/module/*/initstate
/sys/module/*/refcnt
/sys/module/*/sections/*
/sys/module/*/parameters/*
/sys/module/*/holders/*
/sys/module/*/notes/*
/sys/module/*/coresize
/sys/module/*/initsize
/sys/module/*/taint
/sys/module/*/uevent
/sys/module/*/drivers/*
```

`/sys/module/*/parameters/*` — module-parameters — a loaded-module
recon — the driver-view.

## The `/sys/firmware` — the firmware-view

```
/sys/firmware/efi/*
/sys/firmware/efi/vars/*
/sys/firmware/efi/efivars/*
/sys/firmware/efi/systab
/sys/firmware/efi/fw_vendor
/sys/firmware/efi/runtime
/sys/firmware/efi/runtime-map/*
/sys/firmware/efi/mok/*
/sys/firmware/efi/config_table
/sys/firmware/efi/secure_boot
/sys/firmware/efi/smbios/*
/sys/firmware/dmi/entries/*
/sys/firmware/dmi/tables/*
/sys/firmware/acpi/tables/*
/sys/firmware/acpi/interrupts/*
/sys/firmware/acpi/pm_profile
/sys/firmware/acpi/hotplug/*
/sys/firmware/devicetree/*
/sys/firmware/fdt/*
/sys/firmware/fpga/*
/sys/firmware/fpga_manager/*
/sys/firmware/iscsi_boot*
/sys/firmware/iscsi_ibft*
/sys/firmware/memmap/*
/sys/firmware/qemu_fw_cfg/*
/sys/firmware/ras/*
/sys/firmware/sfi/*
/sys/firmware/smbios/*
/sys/firmware/stratix10-svc/*
/sys/firmware/tee/*
/sys/firmware/trusted-firmware/*
/sys/firmware/xen/*
/sys/firmware/xen-dt/*
/sys/firmware/xen-pciback/*
/sys/firmware/xen-vfb/*
/sys/firmware/xen-vkbd/*
/sys/firmware/xen-vms/*
/sys/firmware/xen-xenbus/*
/sys/firmware/xenbus/*
/sys/firmware/zynqmp/*
```

`/sys/firmware/dmi/`+`/sys/firmware/efi/`+`/sys/firmware/acpi/` —
the firmware-view — BIOS/UEFI/ACPI tables — a host-fingerprint.

## The `/dev` special-files — the device-corpus

```
/dev/null /dev/zero /dev/full /dev/random /dev/urandom
/dev/stdin /dev/stdout /dev/stderr
/dev/fd/0 /dev/fd/1 /dev/fd/2 /dev/fd/3 ... /dev/fd/255
/dev/pts/0 /dev/pts/1 /dev/pts/ptmx
/dev/tty /dev/tty0 /dev/tty1 ... /dev/tty63 /dev/ttyS0 /dev/ttyS1 /dev/ttyUSB0
/dev/console
/dev/mem /dev/kmem /dev/port                      — physical-mem — root
/dev/kmsg                                          — dmesg — root
/dev/kcore                                         — kernel-mem — root
/dev/disk/by-id/* /dev/disk/by-path/* /dev/disk/by-uuid/* /dev/disk/by-label/*
/dev/sda /dev/sda1 /dev/sdb /dev/nvme0n1 /dev/nvme0n1p1 /dev/mmcblk0
/dev/mmcblk0p1 /dev/loop0 ... /dev/loop255 /dev/loop-control
/dev/mapper/* /dev/dm-* /dev/lvm/* /dev/md* /dev/md0 /dev/md127
/dev/zram* /dev/ram* /dev/ram0 ... /dev/ram15
/dev/nbd* /dev/nbd0 ... /dev/nbd15
/dev/drbd* /dev/drbd0 ... /dev/drbd15
/dev/cdrom /dev/dvd /dev/cdrw /dev/dvdrw /dev/cdrom0 /dev/sr0 /dev/sr1
/dev/usb/* /dev/bus/usb/* /dev/usbdev* /dev/hidraw* /dev/hidg*
/dev/input/* /dev/input/event* /dev/input/mouse* /dev/input/mice
/dev/input/js* /dev/input/ts* /dev/input/by-id/* /dev/input/by-path/*
/dev/fb0 /dev/fb1 /dev/fb2 /dev/fb3 /dev/dri/* /dev/dri/card* /dev/dri/renderD*
/dev/vga_arbiter /dev/agpgart /dev/dri/card0 /dev/dri/card1 /dev/dri/renderD128
/dev/dri/renderD129 /dev/dri/renderD130 /dev/dri/renderD131 /dev/dri/controlD64
/dev/dri/controlD65 /dev/dri/controlD66 /dev/dri/controlD67 /dev/dri/by-path/*
/dev/dri/by-id/*
/dev/snd/* /dev/snd/pcm* /dev/snd/controlC* /dev/snd/timer /dev/snd/seq
/dev/snd/midi* /dev/snd/midiC*D* /dev/snd/hwC*D* /dev/snd/by-path/* /dev/snd/by-id/*
/dev/video* /dev/video0 /dev/video1 /dev/v4l/* /dev/v4l/by-path/* /dev/v4l/by-id/*
/dev/media* /dev/radio* /dev/vbi* /dev/vbi0 /dev/vbi1
/dev/dvb/* /dev/dvb/adapter* /dev/dvb/adapter0/* /dev/dvb/adapter1/*
/dev/cec* /dev/cec0 /dev/cec1
/dev/i2c* /dev/i2c-0 /dev/i2c-1 /dev/spidev* /dev/spidev0.0 /dev/spidev0.1
/dev/ttyO* /dev/ttyS* /dev/ttyAMA* /dev/ttyUSB* /dev/ttyACM* /dev/ttyGS*
/dev/ttyGS0 /dev/ttyGS1 /dev/ttyGS2 /dev/ttyGS3
/dev/serial/by-id/* /dev/serial/by-path/*
/dev/bluetooth/* /dev/rfkill* /dev/rfkill0 /dev/rfkill1
/dev/ieee80211/* /dev/phy* /dev/phy0 /dev/phy1
/dev/hwmon/* /dev/hwmon/hwmon* /dev/hwmon/hwmon*/* /dev/hwmon/hwmon0/*
/dev/thermal/* /dev/thermal/thermal_zone* /dev/thermal/cooling_device*
/dev/gpiochip* /dev/gpiochip0 /dev/gpiochip1 /dev/gpiochip2 /dev/gpiochip3
/dev/gpiochip4 /dev/gpiochip5 /dev/gpiochip6 /dev/gpiochip7 /dev/gpiochip8
/dev/gpiochip9 /dev/gpiochip10 /dev/gpiochip11 /dev/gpiochip12 /dev/gpiochip13
/dev/gpiochip14 /dev/gpiochip15 /dev/gpiochip16 /dev/gpiochip17 /dev/gpiochip18
/dev/gpiochip19 /dev/gpiochip20 /dev/gpiochip21 /dev/gpiochip22 /dev/gpiochip23
/dev/gpiochip24 /dev/gpiochip25 /dev/gpiochip26 /dev/gpiochip27 /dev/gpiochip28
/dev/gpiochip29 /dev/gpiochip30 /dev/gpiochip31
/dev/mtd* /dev/mtdblock* /dev/mtd0 /dev/mtd0ro /dev/mtdblock0 /dev/mtdblock0ro
/dev/mtd1 /dev/mtd1ro /dev/mtdblock1 /dev/mtdblock1ro /dev/mtd2 /dev/mtd2ro
/dev/mtdblock2 /dev/mtdblock2ro /dev/mtd3 /dev/mtd3ro /dev/mtdblock3 /dev/mtdblock3ro
/dev/mtd4 /dev/mtd4ro /dev/mtdblock4 /dev/mtdblock4ro /dev/mtd5 /dev/mtd5ro
/dev/mtdblock5 /dev/mtdblock5ro /dev/mtd6 /dev/mtd6ro /dev/mtdblock6 /dev/mtdblock6ro
/dev/mtd7 /dev/mtd7ro /dev/mtdblock7 /dev/mtdblock7ro /dev/mtd8 /dev/mtd8ro
/dev/mtdblock8 /dev/mtdblock8ro /dev/mtd9 /dev/mtd9ro /dev/mtdblock9 /dev/mtdblock9ro
/dev/ubi* /dev/ubi0 /dev/ubi0_0 /dev/ubi1 /dev/ubi1_0 /dev/ubi_ctrl
/dev/ubi0_1 /dev/ubi0_2 /dev/ubi0_3 /dev/ubi0_4 /dev/ubi0_5 /dev/ubi0_6 /dev/ubi0_7
/dev/ubi1_1 /dev/ubi1_2 /dev/ubi1_3 /dev/ubi1_4 /dev/ubi1_5 /dev/ubi1_6 /dev/ubi1_7
/dev/nand* /dev/nand0 /dev/nand0a /dev/nand0b /dev/nand0c /dev/nand0d
/dev/nand1 /dev/nand1a /dev/nand1b /dev/nand1c /dev/nand1d
/dev/nor* /dev/nor0 /dev/nor1 /dev/nor2 /dev/nor3
/dev/eeprom* /dev/eeprom0 /dev/eeprom1
/dev/frf* /dev/fram* /dev/nvram* /dev/rtc* /dev/rtc0 /dev/rtc1
/dev/watchdog* /dev/watchdog0 /dev/watchdog1
/dev/hpet /dev/rtc /dev/rtc0 /dev/rtc1
/dev/ppdev* /dev/parport* /dev/parport0 /dev/parport1 /dev/lp* /dev/lp0 /dev/lp1
/dev/ipmi* /dev/ipmi0 /dev/ipmi1 /dev/ipmidev/*
/dev/kvm /dev/vhost-net /dev/vhost-vsock /dev/vhost-scsi /dev/vhost-vdpa*
/dev/vhost-vsock /dev/vhost-net /dev/vhost-scsi /dev/vhost-vdpa0 /dev/vhost-vdpa1
/dev/vsock /dev/vsock0 /dev/vsock1
/dev/tun /dev/tap /dev/net/tun /dev/net/tap
/dev/ppp /dev/pppox* /dev/pppox0 /dev/pppox1
/dev/pppoe* /dev/pppoe0 /dev/pppoe1
/dev/pppo* /dev/pppo0 /dev/pppo1
/dev/pppol2tp* /dev/pppol2tp0 /dev/pppol2tp1
/dev/wan* /dev/wan0 /dev/wan1
/dev/hdlc* /dev/hdlc0 /dev/hdlc1
/dev/capi* /dev/capi20* /dev/capi20.00 /dev/capi20.01
/dev/isdn* /dev/isdn0 /dev/isdn1 /dev/isdninfo /dev/isdnctrl* /dev/isdnctrl0
/dev/isdnctrl1 /dev/ippp* /dev/ippp0 /dev/ippp1
/dev/modem* /dev/modem0 /dev/modem1 /dev/ttyI* /dev/ttyI0 /dev/ttyI1
/dev/cui* /dev/cui0 /dev/cui1
/dev/dsp* /dev/dsp0 /dev/dsp1 /dev/dspW* /dev/dspW0 /dev/dspW1
/dev/audio* /dev/audio0 /dev/audio1 /dev/audioctl* /dev/audioctl0 /dev/audioctl1
/dev/mixer* /dev/mixer0 /dev/mixer1 /dev/midi* /dev/midi0 /dev/midi1
/dev/smp* /dev/smp0 /dev/smp1 /dev/smpte* /dev/smpte0 /dev/smpte1
/dev/adsp* /dev/adsp0 /dev/adsp1 /dev/admmidi* /dev/admmidi0 /dev/admmidi1
/dev/dmmidi* /dev/dmmidi0 /dev/dmmidi1 /dev/music* /dev/music0 /dev/music1
/dev/drm* /dev/drm0 /dev/drm1
/dev/radio* /dev/radio0 /dev/radio1 /dev/radio60 /dev/radio61
/dev/bttv* /dev/bttv0 /dev/bttv1 /dev/bttv-vbi* /dev/bttv-vbi0 /dev/bttv-vbi1
/dev/camera* /dev/camera0 /dev/camera1
/dev/lirc* /dev/lirc0 /dev/lirc1 /dev/lircd
/dev/irda* /dev/irda0 /dev/irda1
/dev/winbond* /dev/winbond0 /dev/winbond1
/dev/efirtc* /dev/efirtc0 /dev/efirtc1
```

The `/dev` corpus — the device-surface — mostly irrelevant to CTF-file-read
but included for completeness — `/dev/std*`/`/dev/fd/*` are the useful
ones (fd-as-file). `/dev/mem`/`/dev/kcore`/`/dev/kmsg` need root.
