import os, re, glob, copy, yaml, json, shutil, xarray as xr
import netCDF4
from datetime import datetime
from melodies_monet import driver

import sys
sys.path.insert(0, "/glade/u/home/lcthompson/mm/MELODIES-MONET/docs/examples/ungridded_support/unstructured_grid_read_uxarray/louisa_asiaaq_cs/asiaaq_cs_06082026/output")


CTRL    = "/glade/u/home/lcthompson/mm/MELODIES-MONET/docs/examples/ungridded_support/unstructured_grid_read_uxarray/louisa_asiaaq_cs/asiaaq_cs_06082026/control_air_full_camp_cesm-se.yaml"
PAIRDIR = "/glade/u/home/lcthompson/mm/MELODIES-MONET/docs/examples/ungridded_support/unstructured_grid_read_uxarray/louisa_asiaaq_cs/asiaaq_cs_06082026/output/pair"
PLOTROOT = "/glade/u/home/lcthompson/mm/MELODIES-MONET/docs/examples/ungridded_support/unstructured_grid_read_uxarray/louisa_asiaaq_cs/asiaaq_cs_06082026/output"
TMPDIR = "/glade/u/home/lcthompson/mm/MELODIES-MONET/docs/examples/ungridded_support/unstructured_grid_read_uxarray/louisa_asiaaq_cs/asiaaq_cs_06082026/output"

os.makedirs(TMPDIR, exist_ok=True)

base = yaml.safe_load(open(CTRL))

_ymd = os.environ.get("YMD")

# swath pairing
_sat = os.environ.get("SAT", "").strip().lower()          # no2 | hcho | co
if _ymd and _sat:
    _SAT_KEYS = {"no2": "tropomi_l2_no2", "hcho": "tropomi_l2_hcho",
                 "co": "tropomi_l2_co"}
    if _sat not in _SAT_KEYS:
        raise SystemExit(f"SAT={_sat!r} must be one of {list(_SAT_KEYS)}")
    key = _SAT_KEYS[_sat]

    target = os.environ.get("REGRID_TARGET", "swath").strip().lower()
    if target not in ("swath", "model", "obs"):
        raise SystemExit(f"REGRID_TARGET={target!r} must be swath|model|obs")
    method = os.environ.get("REGRID_METHOD", "conservative").strip()

    iso = datetime.strptime(_ymd, "%Y%m%d").strftime("%Y-%m-%d")
    cd = copy.deepcopy(base)

    _model = os.environ.get("PAIR_MODEL", "").strip()
    if _model:
        if _model not in cd["model"]:
            raise SystemExit(f"PAIR_MODEL={_model!r} not in {list(cd['model'])}")
        cd["model"] = {_model: cd["model"][_model]}   # pair one model per job
        
    cd["analysis"]["start_time"]      = iso
    cd["analysis"]["end_time"]        = f"{iso} 23:59:00"
    cd["analysis"]["output_dir"]      = PAIRDIR
    cd["analysis"]["output_dir_save"] = PAIRDIR

    if key not in cd["obs"]:
        raise SystemExit(f"{key} missing from control obs block")

    # keep ONLY this satellite product (DC8 + other 2 sats are separate passes)
    for k in list(cd["obs"]):
        if k != key:
            cd["obs"].pop(k, None)

    blk = cd["obs"][key]
    blk["regrid_method"] = method
    blk["regrid_target"] = [target]              # <- swath == native pixels
    blk.setdefault("obs_grid_extent", [90, 135, 0, 45])   # crop for every target

    if target == "swath":
        import numpy as _np, pandas as _pd
        _pad = float(os.environ.get("SWATH_PAD_DEG", "1.0"))
        _dc8 = sorted(glob.glob(f"{PAIRDIR}/asiaaq_{_ymd}_dc8_*.nc4"))
        if _dc8:
            with xr.open_dataset(_dc8[0]) as _d:
                _lo = _np.asarray(_d["longitude"].values, float).ravel()
                _la = _np.asarray(_d["latitude"].values, float).ravel()
                _t  = _np.asarray(_d["time"].values).ravel()      # datetime64
            _lo = _lo[_np.isfinite(_lo)]; _la = _la[_np.isfinite(_la)]
            if _lo.size:
                blk["obs_grid_extent"] = [float(_lo.min()) - _pad, float(_lo.max()) + _pad,
                                          float(_la.min()) - _pad, float(_la.max()) + _pad]
            _t = _t[~_np.isnat(_t)]
            if _t.size:
                _hw = float(os.environ.get("TIME_PAD_HR", "3"))
                t0 = _pd.Timestamp(_t.min()) - _pd.Timedelta(hours=_hw)
                t1 = _pd.Timestamp(_t.max()) + _pd.Timedelta(hours=_hw)
                cd["analysis"]["start_time"] = t0.strftime("%Y-%m-%d %H:%M:%S")
                cd["analysis"]["end_time"]   = t1.strftime("%Y-%m-%d %H:%M:%S")
                print(f"[swath] time window -> {cd['analysis']['start_time']} .. "
                      f"{cd['analysis']['end_time']}", flush=True)
        print(f"[swath] obs_grid_extent -> {blk['obs_grid_extent']}", flush=True)
            
    if target != "obs":
        blk.pop("obs_grid_res", None)            # res only builds the L3 lat/lon grid
        
    day_glob = blk["filename"].replace("202402*", f"{_ymd}T*")
    src = sorted(glob.glob(day_glob))
    if not src:
        raise SystemExit(f"no granules match {day_glob}")
    _mtag = (_model or "allmodels").replace("cam-chem-se-", "")
    good_dir = f"{PAIRDIR}/_granules/{_sat}_{_mtag}_{_ymd}"   # <- per (sat, model, day)
    shutil.rmtree(good_dir, ignore_errors=True)
    os.makedirs(good_dir, exist_ok=True)
    n_bad = 0
    for f in src:
        try:
            with netCDF4.Dataset(f, "r"):
                pass
        except OSError as e:
            n_bad += 1
            print(f"[skip] unreadable granule {os.path.basename(f)}: {e}", flush=True)
            continue
        link = f"{good_dir}/{os.path.basename(f)}"
        if not os.path.lexists(link):        # idempotent: never re-link
            os.symlink(f, link)
    ngood = len(glob.glob(f"{good_dir}/*.nc"))
    print(f"[granules] {_sat} {_ymd}: {ngood} good, {n_bad} skipped", flush=True)
    if ngood == 0:
        raise SystemExit(f"all granules unreadable for {_sat} {_ymd}")
    blk["filename"] = f"{good_dir}/*.nc"

    # restrict model mapping to the kept product so nothing else pairs
    _keep = set(cd["obs"])
    for _m in cd["model"].values():
        if isinstance(_m.get("mapping"), dict):
            _m["mapping"] = {k: v for k, v in _m["mapping"].items() if k in _keep}

    # tag prefix with the grid target so swath & model outputs coexist
    cd["analysis"]["save"]["paired"]["prefix"] = f"asiaaq_{_ymd}_{target}"

    os.makedirs(PAIRDIR, exist_ok=True)
    tmp = f"{PAIRDIR}/control_{target}_{_sat}_{_ymd}.yaml"
    yaml.safe_dump(cd, open(tmp, "w"), sort_keys=False)
    print(f"==== PAIRING TROPOMI {_sat} {iso} [{method}->{target}] ====", flush=True)
    an = driver.analysis()
    an.control = tmp
    an.read_control()
    an.open_models()
    an.open_obs()
    an.pair_data()
    an.save_analysis()
    for label, p in an.paired.items():
        print(f"  {label}: {dict(p.obj.sizes)}", flush=True)
    print(f"paired -> {PAIRDIR}/asiaaq_{_ymd}_{target}_{key}_*", flush=True)
    raise SystemExit(0)
    
if _ymd:
    DC8DIR = "/glade/campaign/acom/acom-weather/emmons/ASIAAQ_obs/DC8"
    iso = datetime.strptime(_ymd, "%Y%m%d").strftime("%Y-%m-%d")
    cd = copy.deepcopy(base)
    cd["analysis"]["start_time"]      = iso
    cd["analysis"]["end_time"]        = f"{iso} 23:59:00"
    cd["analysis"]["output_dir"]      = PAIRDIR
    cd["analysis"]["output_dir_save"] = PAIRDIR
    cd["analysis"]["save"]["paired"]["prefix"] = f"asiaaq_{_ymd}"
    cd["obs"]["dc8"]["filename"] = f"{DC8DIR}/asiaaq-mrg10_dc8_{_ymd}_RA_*.ict"
    for k in ("tropomi_l2_no2", "tropomi_l2_hcho", "tropomi_l2_co"):
        cd["obs"].pop(k, None)          # DC8-only here; TROPOMI is its own pass

    # for future reference, keep satellite, aircraft pairing seperate so things dont conflict. 
    _keep = set(cd["obs"])
    for _m in cd["model"].values():
        if isinstance(_m.get("mapping"), dict):
            _m["mapping"] = {k: v for k, v in _m["mapping"].items() if k in _keep}
        
    os.makedirs(PAIRDIR, exist_ok=True)
    tmp = f"{PAIRDIR}/control_pair_{_ymd}.yaml"
    yaml.safe_dump(cd, open(tmp, "w"), sort_keys=False)
    print(f"==== PAIRING flight {iso} ====", flush=True)
    an = driver.analysis()
    an.control = tmp
    an.read_control()
    an.open_models()
    an.open_obs()
    an.pair_data()
    an.save_analysis()
    
    print(f"paired -> {PAIRDIR}/asiaaq_{_ymd}_dc8_*", flush=True)
    raise SystemExit(0)
    
# # flights that produced paired files 
# dates = sorted(re.search(r'asiaaq_(\d{8})_dc8_', os.path.basename(f)).group(1)
#                for f in glob.glob(f"{PAIRDIR}/asiaaq_*_dc8_cam-chem-se-era5.nc4"))
# print("flights to plot:", dates)

# for ymd in dates:
#     iso = datetime.strptime(ymd, "%Y%m%d").strftime("%Y-%m-%d")
#     cd  = copy.deepcopy(base)

#     outdir = f"{PLOTROOT}/{ymd}"
#     os.makedirs(outdir, exist_ok=True)
#     cd["analysis"]["output_dir"]      = outdir
#     cd["analysis"]["output_dir_save"] = outdir
#     cd["analysis"]["output_dir_read"] = PAIRDIR
#     cd["analysis"]["start_time"]      = iso
#     cd["analysis"]["end_time"]        = f"{iso} 23:59:00"

#     # this flight's two paired files only
#     fn = cd["analysis"]["read"]["paired"]["filenames"]
#     for model in ["cam-chem-se-era5", "cam-chem-se-merra2"]:
#         f = f"{PAIRDIR}/asiaaq_{ymd}_dc8_{model}.nc4"
#         fn[f"dc8_{model}"] = [f] if os.path.exists(f) else []
#     fn = {k: v for k, v in fn.items() if v}              # drop any model w/o a file
#     cd["analysis"]["read"]["paired"]["filenames"] = fn
#     avail = list(fn.keys())                              # pairs present for THIS flight

#     # way to skip variables that were not recorded on flight
#     MODELCOL = {"O3": "O3_new", "CO": "CO_new", "NO2": "NO2_new", "temperature": "T"}   # obs_var to model column
#     COORDS   = {"pressure_obs", "altitude"}                         # always keep (vertical axis)

#     present = set(MODELCOL)
#     for files in fn.values():                       # every available pair file for this flight
#         ds = xr.open_dataset(files[0])
#         dv = set(ds.data_vars)
#         for ov, mcol in MODELCOL.items():
#             if mcol not in dv or int(ds[mcol].count()) == 0:   # model col absent/all-NaN
#                 present.discard(ov)
#         ds.close()
        
#     print(f"   {ymd}: plotting vars -> {sorted(present)}", flush=True)
#     if not present:
#         print(f"   SKIP {ymd}: nothing to plot"); continue

#     PRUNEDIR = f"{TMPDIR}/pruned"
#     os.makedirs(PRUNEDIR, exist_ok=True)
#     new_fn = {}
    
#     for key, files in fn.items():
#         dst = f"{PRUNEDIR}/{ymd}_{os.path.basename(files[0])}"
#         shutil.copyfile(files[0], dst)
#         with netCDF4.Dataset(dst, "a") as nc:
#             meta = json.loads(nc.getncattr("dict_json"))
#             ov, mv = meta["obs_vars"], meta["model_vars"]
#             idx = [i for i, o in enumerate(ov) if o in present]   # keep aligned pairs
#             meta["obs_vars"]   = [ov[i] for i in idx]
#             meta["model_vars"] = [mv[i] for i in idx]
#             nc.setncattr("dict_json", json.dumps(meta))
#         new_fn[key] = [dst]
#     cd["analysis"]["read"]["paired"]["filenames"] = new_fn
    
#     vd = cd["obs"]["dc8"]["variables"]
#     cd["obs"]["dc8"]["variables"] = {k: v for k, v in vd.items() if k in COORDS or k in present}
#     print(f"   {ymd}: plotting vars -> {sorted(present)}", flush=True)
#     if not present:
#         print(f"   SKIP {ymd}: no gas variables present"); continue
        
#     # label every plot/stat with the date, and only reference available pairs
#     for g in cd["plots"].values():
#         g["domain_name"] = [f"DC8 {iso}"]
#         g["data"] = [d for d in g["data"] if d in avail]
#     cd["stats"]["domain_name"] = [f"DC8 {iso}"]
#     cd["stats"]["data"] = [d for d in cd["stats"]["data"] if d in avail]

#     tmp = f"{TMPDIR}/control_dc8_plot_{ymd}.yaml"
#     yaml.safe_dump(cd, open(tmp, "w"), sort_keys=False)

#     print(f"==== plotting flight {iso} ====", flush=True)
#     an = driver.analysis()
#     an.control = tmp
#     an.read_control()
    
#     an.open_models()
#     an.open_obs()
#     an.pair_data()
#     an.save_analysis()

#     # an.read_analysis()
#     # an.plotting()
#     # an.stats()
