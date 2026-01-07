import numpy as np
from plyfile import PlyData
from litemapy import Region, Schematic, BlockState
import os
import colorsys

# ================= 配置区域 (Configuration) =================
# --- 输入与输出 ---
INPUT_PLY = "test.ply"  # 输入的 .ply 文件，带后缀
OUTPUT_NAME = "output_model"  # 输出文件名，不带后缀

# --- 核心生成参数 ---
SCALE_FACTOR = 100.0  # 缩放比例 (越大建筑越大)
INVERT_Y_AXIS = True  # 是否反转Y轴 (解决建筑倒置问题)
MIRROR_X_AXIS = True  # 是否反转X轴 (解决建筑左右镜像问题)

# --- 过滤参数 ---
DENSITY_THRESHOLD = 0.2  # 密度阈值 (0.0-1.0)，越小方块越多，越大越镂空
MIN_OPACITY_CUTOFF = 0.01  # 忽略不透明度低于此值的点 (去除背景噪点)

# --- 颜色与过滤参数 ---
SATURATION_BOOST = 1.5       # 色彩饱和度倍增 (1.0=原色, 1.5=鲜艳, 2.0=非常鲜艳)
MIN_NEIGHBORS = 1            # 孤立点去除：如果一个方块周围少于多少个方块，则删除它

# ================= 方块调色板 (配置区域) =================
# 包含：所有木材(含樱花/苍白橡木)、混凝土、陶瓦、石材等，可根据需求增减
# 格式: "minecraft:block_id": (R, G, B)
BLOCK_PALETTE = {
    # --- 木材类 (Logs & Woods) ---
    "minecraft:acacia_log": (103, 96, 86),
    "minecraft:acacia_planks": (169, 91, 50),
    "minecraft:stripped_acacia_wood": (174, 92, 59),

    "minecraft:birch_wood": (214, 214, 210),
    "minecraft:birch_planks": (192, 175, 121),
    "minecraft:stripped_birch_wood": (196, 176, 118),

    "minecraft:cherry_wood": (62, 34, 39),
    "minecraft:cherry_planks": (224, 172, 189),  # 粉色木板
    "minecraft:stripped_cherry_wood": (229, 179, 195),

    "minecraft:dark_oak_wood": (60, 47, 26),
    "minecraft:dark_oak_planks": (66, 43, 20),
    "minecraft:stripped_dark_oak_wood": (67, 49, 30),

    "minecraft:jungle_wood": (85, 68, 25),
    "minecraft:jungle_planks": (160, 115, 80),
    "minecraft:stripped_jungle_wood": (172, 128, 86),

    "minecraft:mangrove_wood": (82, 57, 47),
    "minecraft:mangrove_planks": (118, 54, 49),
    "minecraft:stripped_mangrove_wood": (118, 54, 49),

    "minecraft:oak_wood": (115, 89, 52),
    "minecraft:oak_planks": (162, 130, 78),
    "minecraft:stripped_oak_wood": (177, 144, 86),

    "minecraft:spruce_wood": (58, 37, 16),
    "minecraft:spruce_planks": (114, 84, 56),
    "minecraft:stripped_spruce_wood": (114, 86, 51),

    "minecraft:pale_oak_wood": (118, 118, 118),
    "minecraft:pale_oak_planks": (227, 222, 212),
    "minecraft:stripped_pale_oak_wood": (220, 218, 210),

    "minecraft:bamboo_planks": (198, 179, 74),
    "minecraft:stripped_bamboo_block": (198, 185, 88),

    # --- 混凝土 (Concrete - 高饱和度) ---
    "minecraft:white_concrete": (207, 213, 214),
    "minecraft:orange_concrete": (224, 97, 1),
    "minecraft:magenta_concrete": (169, 48, 159),
    "minecraft:light_blue_concrete": (35, 137, 198),
    "minecraft:yellow_concrete": (240, 175, 21),
    "minecraft:lime_concrete": (94, 169, 24),
    "minecraft:pink_concrete": (213, 101, 142),
    "minecraft:gray_concrete": (54, 57, 61),
    "minecraft:light_gray_concrete": (125, 125, 115),
    "minecraft:cyan_concrete": (21, 119, 136),
    "minecraft:purple_concrete": (100, 31, 156),
    "minecraft:blue_concrete": (44, 46, 143),
    "minecraft:brown_concrete": (96, 59, 31),
    "minecraft:green_concrete": (73, 91, 36),
    "minecraft:red_concrete": (142, 32, 32),
    "minecraft:black_concrete": (8, 10, 15),

    # --- 陶瓦 (Terracotta - 低饱和度/自然色) ---
    "minecraft:terracotta": (152, 94, 67),
    "minecraft:white_terracotta": (209, 177, 161),
    "minecraft:orange_terracotta": (161, 83, 37),
    "minecraft:magenta_terracotta": (149, 88, 108),
    "minecraft:light_blue_terracotta": (113, 108, 137),
    "minecraft:yellow_terracotta": (186, 133, 35),
    "minecraft:lime_terracotta": (103, 117, 52),
    "minecraft:pink_terracotta": (161, 78, 78),
    "minecraft:gray_terracotta": (57, 42, 35),
    "minecraft:light_gray_terracotta": (135, 107, 98),
    "minecraft:cyan_terracotta": (86, 91, 91),
    "minecraft:purple_terracotta": (118, 69, 86),
    "minecraft:blue_terracotta": (74, 59, 91),
    "minecraft:brown_terracotta": (77, 51, 35),
    "minecraft:green_terracotta": (76, 83, 42),
    "minecraft:red_terracotta": (142, 60, 46),
    "minecraft:black_terracotta": (37, 22, 16),

    # --- 石材与自然方块 (Stones & Nature) ---
    "minecraft:stone": (125, 125, 125),
    "minecraft:cobblestone": (80, 80, 80),
    "minecraft:smooth_stone": (158, 158, 158),

    "minecraft:andesite": (134, 134, 134),
    "minecraft:polished_andesite": (134, 134, 134),

    "minecraft:diorite": (188, 188, 188),
    "minecraft:polished_diorite": (188, 188, 188),

    "minecraft:blackstone": (45, 37, 43),
    "minecraft:polished_blackstone": (45, 37, 43),
    "minecraft:polished_blackstone_bricks": (39, 33, 38),

    "minecraft:calcite": (224, 224, 220),
    "minecraft:quartz_block": (235, 229, 222),

    "minecraft:sandstone": (218, 210, 158),
    "minecraft:smooth_sandstone": (218, 210, 158),
    "minecraft:red_sandstone": (191, 103, 33),

    "minecraft:dirt": (134, 96, 67),
    "minecraft:end_stone": (221, 223, 165),
}
# ==========================================================

def get_closest_block(r, g, b):
    """计算颜色距离，返回最近似的方块ID"""
    min_dist = float('inf')
    best_block = "minecraft:stone"  # 默认兜底

    target = np.array([r, g, b])

    for block_id, color in BLOCK_PALETTE.items():
        current = np.array(color)
        dist = np.linalg.norm(target - current)  # 欧氏距离
        if dist < min_dist:
            min_dist = dist
            best_block = block_id

    return best_block


def save_litematic(coords, block_names):
    """保存为 .litematic 格式 (已修复 API 调用)"""
    filename = f"{OUTPUT_NAME}.litematic"
    print(f"正在导出到 {filename}")

    if len(coords) == 0:
        print("无方块可保存")
        return

    # 获取边界
    min_x, min_y, min_z = np.min(coords, axis=0)
    max_x, max_y, max_z = np.max(coords, axis=0)

    width = int(max_x - min_x + 1)
    height = int(max_y - min_y + 1)
    length = int(max_z - min_z + 1)

    print(f"投影体积: {width}x{height}x{length}")

    # 创建 Region
    reg = Region(0, 0, 0, width, height, length)
    schem = Schematic(name=OUTPUT_NAME, author="3DGS-Converter", regions={'main': reg})

    count = 0
    for i in range(len(coords)):
        # 转换为相对坐标
        x = int(coords[i][0] - min_x)
        y = int(coords[i][1] - min_y)
        z = int(coords[i][2] - min_z)

        block_id = block_names[i]

        try:
            reg[x, y, z] = BlockState(block_id)
            count += 1
        except Exception as e:
            pass  # 忽略个别错误

    schem.save(filename)
    print(f"完成! 成功保存 {count} 个方块数据")
    print(f"已导出到: {OUTPUT_NAME}.litematic")


def process_gaussian_to_grid():
    if not os.path.exists(INPUT_PLY):
        print(f"错误: 文件 {INPUT_PLY} 不存在！")
        return
    print("正在加载PLY文件...")
    plydata = PlyData.read(INPUT_PLY)
    vertex = plydata['vertex']

    x = np.asarray(vertex['x'])
    y = np.asarray(vertex['y'])
    z = np.asarray(vertex['z'])

    if INVERT_Y_AXIS:
        y = -y

    if MIRROR_X_AXIS:
        x = -x

    # --- 颜色读取与饱和度增强 ---
    try:
        r = np.asarray(vertex['red']).astype(float)
        g = np.asarray(vertex['green']).astype(float)
        b = np.asarray(vertex['blue']).astype(float)
    except:
        SH_C0 = 0.28209479177387814
        r = (0.5 + SH_C0 * np.asarray(vertex['f_dc_0'])) * 255
        g = (0.5 + SH_C0 * np.asarray(vertex['f_dc_1'])) * 255
        b = (0.5 + SH_C0 * np.asarray(vertex['f_dc_2'])) * 255
    # 简单的不透明度处理
    opacity = np.asarray(vertex['opacity'])
    opacity = 1 / (1 + np.exp(-opacity))
    # 初步过滤
    valid_mask = opacity > MIN_OPACITY_CUTOFF
    points_idx = np.where(valid_mask)[0]

    print(f"正在处理 {len(points_idx)} 个有效点...")
    # --- 体素化逻辑 (加权平均) ---
    voxel_map = {}
    for idx in points_idx:
        # 坐标离散化
        gx = int(x[idx] * SCALE_FACTOR)
        gy = int(y[idx] * SCALE_FACTOR)
        gz = int(z[idx] * SCALE_FACTOR)
        coord = (gx, gy, gz)

        op = opacity[idx]

        # 颜色增强：提升每个点的饱和度
        cr, cg, cb = r[idx], g[idx], b[idx]

        # 如果开启了饱和度增强
        if SATURATION_BOOST != 1.0:
            h, s, v = colorsys.rgb_to_hsv(cr / 255.0, cg / 255.0, cb / 255.0)
            s = min(1.0, s * SATURATION_BOOST)  # 增加饱和度
            cr, cg, cb = colorsys.hsv_to_rgb(h, s, v)
            cr, cg, cb = cr * 255, cg * 255, cb * 255
        # 累加颜色 (使用不透明度作为权重，越实的点颜色权重越高)
        if coord not in voxel_map:
            voxel_map[coord] = {
                'accum_r': cr * op,
                'accum_g': cg * op,
                'accum_b': cb * op,
                'accum_op': op,
                'count': 1
            }
        else:
            d = voxel_map[coord]
            d['accum_r'] += cr * op
            d['accum_g'] += cg * op
            d['accum_b'] += cb * op
            d['accum_op'] += op
            d['count'] += 1
    final_coords = []
    final_blocks = []

    # 临时存储用于去噪检查
    temp_blocks = {}  # coord -> block_id
    print("分析体素中...")
    for coord, data in voxel_map.items():
        # 这里的密度阈值逻辑稍微修改：平均密度
        avg_density = data['accum_op']  # 这里用累积密度，类似于"厚度"

        if avg_density > DENSITY_THRESHOLD:
            # 计算加权平均色
            total_weight = data['accum_op']
            if total_weight == 0: continue

            avg_r = data['accum_r'] / total_weight
            avg_g = data['accum_g'] / total_weight
            avg_b = data['accum_b'] / total_weight

            block = get_closest_block(avg_r, avg_g, avg_b)
            temp_blocks[coord] = block
    # --- 孤立点去噪 (Despeckle) ---
    print(f"孤立点去噪 (最少相邻点: {MIN_NEIGHBORS})...")
    kept_count = 0

    # 邻居偏移量 (上下左右前后)
    neighbors_offset = [
        (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)
    ]
    for coord, block_id in temp_blocks.items():
        # 如果不需要去噪，直接添加
        if MIN_NEIGHBORS <= 0:
            final_coords.append(coord)
            final_blocks.append(block_id)
            continue

        # 检查邻居数量
        neighbor_count = 0
        cx, cy, cz = coord
        for dx, dy, dz in neighbors_offset:
            if (cx + dx, cy + dy, cz + dz) in temp_blocks:
                neighbor_count += 1

        # 只有邻居够多才保留
        if neighbor_count >= MIN_NEIGHBORS:
            final_coords.append(coord)
            final_blocks.append(block_id)
            kept_count += 1

    if MIN_NEIGHBORS > 0:
        print(f"共减少 {len(temp_blocks)-kept_count} 个方块")
    save_litematic(np.array(final_coords), final_blocks)


if __name__ == "__main__":
    process_gaussian_to_grid()
