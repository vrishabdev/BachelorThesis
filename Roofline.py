import numpy as np
import matplotlib.pyplot as plt
from fractions import Fraction

I_values = np.logspace(np.log2(0.5), np.log2(8192), 200, base=2)

# TIME values
max_flops_time = 1.0176e12 #Flops/s
memory_bandwidth = 3.195e10 #Byte/s
tau_flop = 1 / max_flops_time #s/Flop
tau_mem = 1 / memory_bandwidth #s/Byte
time_balance_point = tau_mem / tau_flop #Flops/Byte

# ENERGY values
max_flops_energy = 2.664e11 / 11.88 # 22,424GFlops
pi0 = 3.86 #Joule
epsilon_mem = 30.12 / 8e8 #Joule/Byte
epsilon_flop = 11.88 / 2.664e11 #Joule/Flop
energy_balance_point = epsilon_mem / epsilon_flop #Flops/Joule

constant_energy_per_flop = pi0 * tau_flop
actual_energy_per_flop = epsilon_flop + constant_energy_per_flop
constant_flop_energy_efficiency = epsilon_flop / actual_energy_per_flop
effective_energy_balance = constant_flop_energy_efficiency * energy_balance_point
effective_energy_balance += (1 - constant_flop_energy_efficiency) * (np.maximum(0, time_balance_point - I_values))

# POWER values
pi_flop = epsilon_flop / tau_flop

# Roofline Model - TIME
P_values = np.minimum(1, I_values / time_balance_point)  

plt.figure(figsize=(8, 6))
plt.loglog(I_values, P_values, label='Roofline (TFLOP/s)', color='red')

plt.axvline(time_balance_point, linestyle='--', color='black', alpha=0.6)
plt.text(time_balance_point * 1.2, 1/140, f'{time_balance_point:.1f}', color='red')

# Roofline Model - ENERGY
P_values = 1 / (1 + effective_energy_balance / I_values)

plt.loglog(I_values, P_values, label='Arch line (GFLOP/J)', color='blue')

plt.axvline(energy_balance_point, linestyle='--', color='black', alpha=0.6)
plt.text(energy_balance_point * 1.2, 1/140, f'{energy_balance_point:.1f}', color='blue')

xticks = [0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
yticks = [1/2048, 1/1024, 1/512, 1/256, 1/128, 1/64, 1/32, 1/16, 1/8, 1/4, 1/2, 1]
plt.xticks(xticks, [f"{x:.0f}" for x in xticks], fontsize=6)
plt.yticks(yticks, [str(Fraction(y).limit_denominator()) for y in yticks], fontsize=6)

plt.xlabel('Operational Intensity (Flop/Byte)')
plt.ylabel('Relative Performance (1017 GFLOP/s or 22,4 GFLOP/J)')
plt.title('Roofline Model (Intel Core i9-13900K Processor)')
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

def plot(W, Q, benchmark):
    OI = W / Q
    T = max(W * tau_flop, Q * tau_mem)
    P_time = (W / T) / max_flops_time
    plt.scatter(OI, P_time, color='red', label=benchmark, s=6)
    plt.text(OI * 1.1, P_time, benchmark, fontsize=10)

    E = W * epsilon_flop + Q * epsilon_mem + pi0 * T
    P_energy = (W / E) / max_flops_energy
    plt.scatter(OI, P_energy, color='blue', label=benchmark, s=6)
    plt.text(OI * 1.1, P_energy, benchmark, fontsize=10)

# didn't multiply packed_b128_double * 2, because 'Vectorization over 1 doubles = 64 bits (disabled)'
# ran step-48 with 2 cores -> 20_400_000 read and 7_600_000 write operations, so an OI ~85
plot(139_640_372_138 + 13_683_562_268, (11_273_513 + 5_571_360) * 64, "Step-48")

plot(165_367_458 + (79_758_605 * 2), (822_679 + 260_175) * 64, "Step-6")
plot(3_060_227_507 + (3_243_934_680 * 2), (59_576_674 + 35_191_217) * 64, "Step-23")
plot(22_393_784 + (8_293_241 * 2), (689_288 + 191_455) * 64, "Step-61")

# has both single and double precision Flops, but single > double, so counted only single:
plot(50_550_119_919 + (507_296_982 * 4), (134_743_918 + 46_150_212) * 64, "Step-37")

#plot(1_659_750_970 + 24_590_181, (4_382_992 + 1_066_678) * 64, "CG-A")
plot(54_613_840_828 + 588_243_691, (2_277_523_624 + 11_692_672) * 64, "CG-B")
plot(143_528_836_761 + (1_174_935_333 * 2), (13_287_362_119 + 45_536_030) * 64, "CG-C")

plt.savefig("roofline.png")

# Roofline Model - Power
temp = pi_flop / constant_flop_energy_efficiency
temp2 = np.minimum(I_values, time_balance_point) / time_balance_point
temp2 += (effective_energy_balance / np.maximum(I_values, time_balance_point))
P_values = (temp * temp2) / pi_flop

plt.figure(figsize=(8, 6))
plt.loglog(I_values, P_values, label='Power line', color='black')

plt.axvline(time_balance_point, linestyle='--', color='red', alpha=0.6)
plt.text(time_balance_point * 1.2, 1.4, f'{time_balance_point:.1f}', color='red')

plt.axvline(energy_balance_point, linestyle='--', color='blue', alpha=0.6)
plt.text(energy_balance_point * 1.2, 1.4, f'{energy_balance_point:.1f}', color='blue')

plt.axhline(1, linestyle='--', color='black', alpha=0.6)
plt.text(x=1, y=1*1.05, s=f'{pi_flop:.0f} W', color='black')

y = (energy_balance_point / time_balance_point)
plt.axhline(y, linestyle='--', color='black', alpha=0.6)
plt.text(x=1, y=y*1.05, s=f'{y * pi_flop:.0f} W', color='black')

y = 1 + (energy_balance_point / time_balance_point)
plt.axhline(y, linestyle='--', color='black', alpha=0.6)
plt.text(x=3, y=y*1.05, s=f'{y * pi_flop:.0f} W', color='black')

xticks = [0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
yticks = [0.5, 1, 5, 10, 25, 50]
plt.xticks(xticks, [f"{x:.0f}" for x in xticks], fontsize=6)
plt.yticks(yticks, [f"{y:.0f}" for y in yticks], fontsize=6)

plt.xlabel('Operational Intensity (Flop/Byte)')
plt.ylabel(f'Power (Normalized to {pi_flop:.0f} Watt)')
plt.title('Powerline Model (Intel Core i9-13900K Processor)')
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

def plotPower(W, Q, benchmark):
    OI = W / Q
    T = max(W * tau_flop, Q * tau_mem)
    E = W * epsilon_flop + Q * epsilon_mem + pi0 * T
    P = (E / T) / pi_flop
    print(P * pi_flop)
    plt.scatter(OI, P, color='black', label=benchmark, s=6)
    plt.text(OI * 1.1, P, benchmark, fontsize=10)

plotPower(139_640_372_138 + 13_683_562_268, (11_273_513 + 5_571_360) * 64, "Step-48")
plt.savefig("powerline.png")


# perf stat -r5 -e fp_arith_inst_retired.scalar_single,fp_arith_inst_retired.scalar_double,fp_arith_inst_retired.128b_packed_single,fp_arith_inst_retired.128b_packed_double ./step-48
# perf stat -r5 -e unc_m_cas_count_rd,unc_m_cas_count_wr ./step-48
# mem_load_retired.l3_miss
# mem_load_retired.l1_miss,mem_load_retired.l2_miss,mem_load_retired.l3_miss
# 1.989.165.622 + 653.022.314 + 1.340.244 = 2643528180

#uncore_imc_free_running/data_read/                  [Kernel PMU event]
#uncore_imc_free_running/data_total/                 [Kernel PMU event]
#uncore_imc_free_running/data_write/                 [Kernel PMU event]    
