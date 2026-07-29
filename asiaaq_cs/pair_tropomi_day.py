import os, yaml
from melodies_monet import driver

BASE    = "/glade/u/home/lcthompson/mm/MELODIES-MONET/docs/examples/ungridded_support/unstructured_grid_read_uxarray/louisa_asiaaq_cs/asiaaq_cs_06082026/control_air_full_camp_cesm-se.yaml"
PAIRDIR = "/glade/u/home/lcthompson/mm/MELODIES-MONET/docs/examples/ungridded_support/unstructured_grid_read_uxarray/louisa_asiaaq_cs/asiaaq_cs_06082026/output/pair"
TROP    = "/glade/campaign/acom/satellite/tropomi"

ymd = os.environ["YMD"]
iso = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]}"

cd = yaml.safe_load(open(BASE))
cd["analysis"]["start_time"]      = iso
cd["analysis"]["end_time"]        = f"{iso} 23:59:00"
cd["analysis"]["output_dir"]      = PAIRDIR
cd["analysis"]["output_dir_save"] = PAIRDIR
cd["analysis"]["save"]["paired"]["prefix"] = f"asiaaq_{ymd}"

cd["obs"].pop("dc8", None)                          # TROPOMI-only pass
for k in list(cd["obs"]):
    if not k.startswith("tropomi_l2"):
        cd["obs"].pop(k) 

# prune your batch jobs to do 1 day, 1 product, 1 model, per job
_obs_only = os.getenv("PAIR_OBS")
if _obs_only:
    if _obs_only not in cd["obs"]:
        raise SystemExit(f"PAIR_OBS={_obs_only!r} not in control obs: {list(cd['obs'])}")
    cd["obs"] = {_obs_only: cd["obs"][_obs_only]}

_only = os.getenv("PAIR_MODEL")
if _only:
    if _only not in cd["model"]:
        raise SystemExit(f"PAIR_MODEL={_only!r} not in control models: {list(cd['model'])}")
    cd["model"] = {_only: cd["model"][_only]}

_keep = set(cd["obs"])
for _m in cd["model"].values():
    if isinstance(_m.get("mapping"), dict):
        _m["mapping"] = {k: v for k, v in _m["mapping"].items() if k in _keep}
        
day_glob = {
    "tropomi_l2_no2":  f"{TROP}/no2/S5P_OFFL_L2__NO2____{ymd}*.nc",
    "tropomi_l2_hcho": f"{TROP}/hcho/S5P_OFFL_L2__HCHO___{ymd}*.nc",
    "tropomi_l2_co":   f"{TROP}/co/S5P_OFFL_L2__CO_____{ymd}*.nc",
}
for k, g in day_glob.items():
    if k in cd["obs"]:
        cd["obs"][k]["filename"] = g                # narrow to this day's granules

os.makedirs(PAIRDIR, exist_ok=True)
tmp = f"{PAIRDIR}/control_tropomi_{ymd}.yaml"
yaml.safe_dump(cd, open(tmp, "w"), sort_keys=False)

an = driver.analysis(); an.control = tmp; an.read_control()
an.open_models(); an.open_obs(); an.pair_data(); an.save_analysis()
print(f"paired TROPOMI {iso} -> {PAIRDIR}/asiaaq_{ymd}_tropomi_l2_*", flush=True)