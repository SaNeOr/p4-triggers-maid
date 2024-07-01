from trigger.p4_trigger import Whitelist, TriggerFilter

__include_set = [
    "^//repo/release",
]

__exclude_set = [
    ".*/Plugins/.*",
]

__white_list = [
    Whitelist(
        [
            "//repo/release",
        ],
        [
            'maid',
        ]
    ),
]

trigger_filter = TriggerFilter(
    include_set=__include_set,
    white_list=__white_list
)
