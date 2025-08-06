This is a markdown file that uses Latek for the math formulas, best used in Obsidian notebook

## Introduction – Finding the Optimal DPI Using Minimax Cost

Determining the _optimal DPI setting_ for a gaming mouse is a more intricate problem than it first appears. While many gamers rely on intuition, anecdotal experiences, or simply copy professional players, this approach often fails to consider the underlying physics of mouse sensors and the trade-off between _smooth tracking_ and _input reliability_.

Most modern sensors operate best at specific native CPI steps (commonly 400, 800, 1600, 3200, 6400). Using DPI values outside these native steps often leads to **interpolation artifacts**, jitter, or inconsistent tracking, due to internal sensor firmware approximating intermediate values. Therefore, we restrict our search for optimal DPI to these native values.

The optimization problem itself stems from two competing objectives:

### Objective A – Precision

Higher DPI provides finer resolution per inch, enabling smoother crosshair movement. This becomes especially valuable for high-sensitivity players (high eDPI), who rely on **minimal physical movement** to track targets. Smooth motion is crucial in flick-heavy or high-tempo games where responsiveness takes priority over pixel-perfect precision.

### Objective B – Reliability

On the other hand, increased DPI typically degrades the **Signal-to-Noise Ratio (SNR)** of the sensor. At higher resolutions, the sensor becomes more sensitive to micro-movements, tremors, or imperfections in its signal path — amplifying unwanted "noise" and reducing the sensor’s ability to distinguish between intentional input and random variance. This degradation in SNR leads to poorer tracking consistency and jitter. Thus, lower DPI is often **more stable**, particularly at the native resolution where sensor fidelity is highest (usually 400 DPI).

So this framework is based under the assumption that these 2 variables are the only deterministic data for choosing the right DPI.

## Why eDPI Matters for Weighting

A player's **eDPI** (DPI × in-game sensitivity) acts as a metric that reflects **how physically sensitive** their setup is. Rather than comparing DPI in isolation, eDPI aligns more closely with actual crosshair speed and the style of gameplay. Importantly:

- **Low eDPI players** tend to rely on large arm movements for precision — they prioritize sensor **reliability** and consistency. Thus, **SNR should dominate** in the cost function.

- **High eDPI players** use subtle wrist motions with very small physical inputs — they benefit more from higher DPI as it captures nuanced, smooth transitions. Therefore, **precision should dominate** for them.

This is an assumption based on the observation that the "meta DPI" that pro's use differ between games, where Call Of Duty and Fortnite often have a higher average in DPI among professionals as opposed to Counterstrike.

To reflect this trade-off, we design a **weighting function that asymptotically increases** the influence of DPI (Objective A) as eDPI increases. This transition ensures that:

- At low eDPI, the model prefers lower DPI settings that maximize reliability (high SNR).
- At high eDPI, the model gradually favors DPI values that maximize precision (sensor resolution).

---

This framework provides a **principled approach** for DPI selection by casting the problem as a **minimax optimization**, weighted by a player’s gameplay style (via eDPI), and grounded in real sensor performance (via SNR measurements) and should be flexible enough to accommodate a large selection of video games. The result is a tailored DPI recommendation that balances sensor reliability and movement.


## 1. **Objective A – Cost Derived from DPI**

I define **higher DPI** to be better for **Objective A**, so the cost to maximise is:
$$
\text{Cost}_A(D) = 1 - \frac{D}{D_{\text{max}}}
$$
- $D$ = current DPI under consideration
- $D_{max}$​ = highest DPI in my evaluation range (e.g. 6400)

This normalises the precision cost from **1.0 (worst, at lowest DPI)** to **0.0 (best, at highest DPI)**


## 2. **Objective B – Cost Derived from SNR**

I define a cost function based on SNR, which I denote as $\text{Cost}_{\text{B}}$​ , where **lower SNR is worse**, and the objective is to minimise:
$$
\text{Cost}_{\text{B}}(D) = 1 - \frac{\text{SNR}(D)}{\text{SNR}_{\text{max}}}
$$
- $\text{SNR}(D)$= measured $\text{SNR}$ to compare at subject DPI
- $\text{SNR}_{max}​$ = highest observed $\text{SNR}$ (usually at 400 DPI)

This normalises the reliability cost from **0.0 (best SNR)** to **1.0 (worst SNR)**.


## 3. **Weighting the Objectives – Asymptotic Growth Based on eDPI**

We define $w_A(e)$ , the weight on **Objective A**, to **asymptotically increase** with the player's eDPI:
$$
w_A(e) = w_{A,\text{max}} \cdot \left( 1 - e^{-\alpha (e - e_0)} \right)
$$
Where:
- $e=\text{eDPI}=D×\text{ingame sensitivity}$
- $e_0$ = lowest $\text{eDPI}$  (e.g. 400)
- $w_{A,max}∈(0,1)$ = asymptotic upper bound of $w_A$ (e.g. 0.85)
- $α>0$ = growth rate (e.g. 0.001–0.005 depending on the curve steepness)

Then:
$$
w_B(e)=1−w_A(e)​
$$
This guarantees:
- At low eDPI:  $w_B$  ≈ 1.0 -> prioritises reliability (SNR)
- At high eDPI:  $w_A$ -> $w_{A,\text{max}}$ -> prioritises smooth mouse movements (DPI)

## 4. **Final Minimax Cost Function**

We now define the **total cost function** as a minimax over the two weighted objectives:
$$
\text{TotalCost}(D) = \max \left( w_A(e) \cdot \text{Cost}_A(D),\; w_B(e) \cdot \text{Cost}_B(D) \right)
$$
And the optimal DPI is given by:
$$
D^* = \arg\min_D \text{TotalCost}(D)
$$
Where:
- $D$ ∈ **{400, 800, 1600, 3200, 6400}** (native CPI steps)
- $D^*$ = optimal DPI value


## **Example Plug-in Values**

Assume the following:
- $D_{max}$ = 6400
- $SNR(400)$ = 0.95,  $\text{SNR}(800)$ = 0.90, etc.
- ${w}_\text{A,max}$ = 0.85
- $\alpha$ = 0.002
- Player's eDPI (unit of measurement Counter Strike 2) = 800

Then:
1. Compute $w_A$ (800)
2. Get corresponding $w_B$ = 1 - ​$w_A$
3. Calculate $Cost_A(D)$ for each DPI
4. Calculate $Cost_{B}(D)$ for each DPI
5. Plug into minimax:
$$
\text{TotalCost}(D) = \max \left( w_A \cdot \text{Cost}_A(D),\; w_B \cdot \text{Cost}_B(D) \right)
$$
6. Pick DPI with the **lowest TotalCost**


---

## **Data Aquisition**

To measure SNR in the context of mouse sensors:
- **Signal** = actual motion intended by the user.
- **Noise** = unintended motion (e.g. jitter, drift, sensor error, hand vibration).
- **SNR** is calculated as:
$$
\text{SNR} = \frac{\sigma^2_{\text{signal}}}{\sigma^2_{\text{noise}}}
$$
To measure SNR use a Mouse Data Logging Tool use tools like:
- **MouseTester** (Windows GUI for raw delta recording)
- **Interception driver + Python script** for raw `dx/dy` polling
- **RawInputRecorder** or custom C++ tools via Win32 API

These tools give you **raw motion deltas** (x/y) from the mouse at a constant polling rate.


### Step 1: Measure **Noise** (No Movement)

1. Set the mouse **completely still** on a hard, consistent surface.
2. Log at least **5–10 seconds** of data per DPI step.
3. Compute:
$$
\sigma^2_{\text{noise}} = \text{Var}(\Delta x) + \text{Var}(\Delta y)
$$
This gives you the **noise floor** of the sensor at that DPI.

### Step 2: Measure **Signal** (Controlled Movement)

1. Slowly and smoothly move the mouse **in a straight line**.
2. Log movement data again for 5–10 seconds.
3. Compute:
$$
\sigma^2_{\text{signal}} = \text{Var}(\Delta x) + \text{Var}(\Delta y)
$$
This reflects the **combined motion and error**, i.e. signal + noise.

### Step 3: Compute SNR

Now compute:
$$
\text{SNR} = \frac{\sigma^2_{\text{signal}}}{\sigma^2_{\text{noise}}}
$$
Repeat this process for all **DPI steps** (e.g., 400, 800, 1600, 3200, 6400).

---

## **Conclusion and Usage**

In the Python code I assume SNR values, these are not actual recordings. Once actual SNR values are derived and used in `snr_values` array then modify:

- `e0`: This is the reference eDPI value where the weight on Objective A (DPI smoothness) begins to **significantly increase**.
- `w_A_max`: The **ceiling weight** assigned to precision (Objective A), even at very high eDPI.
- `alpha`: Controls **how quickly** the weighting transitions from SNR-focused to DPI-focused as eDPI increases.

These parameters are apart of the weighting function used to control how much importance is given to **Objective A** versus **Objective B** based on the users eDPI. These parameters play a central role to the outcome and allow the function to adapt to different user styles in a given video game. To find the right parameters you can adjust them so it is roughly what actual pro player's use as their preffered DPI settings, essentially using wisdom of the crowd to find the best values for these 3 parameters, and once you have the parameter values it should be general enough to apply to a wide range of mouses and eDPI values.

