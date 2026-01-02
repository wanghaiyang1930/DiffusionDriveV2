export PYTHONPATH=$PWD:$PYTHONPATH
python ./navsim/planning/script/run_pdm_score_fast.py \
        agent=diffusiondrivev2_sel_agent \
        experiment_name=diffusiondrivev2_agent_eval \
        train_test_split=mini \
        agent.checkpoint_path=ckpts/DiffusionDriveV2/diffusiondrivev2_sel.ckpt \
        +metric_cache_path="${NAVSIM_EXP_ROOT}/metric_cache/" \
        +test_cache_path="${NAVSIM_EXP_ROOT}/metric_feature_cache/"
