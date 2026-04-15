# QGIS APP Dinâmica / Dynamic Riparian Buffer
Ferramenta para QGIS que gera APP automaticamente com base na largura do rio conforme o Código Florestal brasileiro — QGIS tool for automatic delineation of Permanent Preservation Areas (APP – legally protected riparian buffer zones in Brazil) based on river width.

## Contexto e Motivação / Context and Motivation

**PORTUGUÊS**
Este projeto foi desenvolvido a partir de demandas em projetos de planejamento urbano e ambiental, especialmente na delimitação de Áreas de Preservação Permanente (APP) em cursos d’água.

Na prática, a definição de APPs é frequentemente realizada de forma manual ou com métodos simplificados, o que pode gerar inconsistências, baixa reprodutibilidade e alto tempo de processamento, principalmente em áreas extensas ou com grande quantidade de cursos d'água.

Além disso, a largura dos cursos d’água varia ao longo do seu percurso, o que exige uma abordagem mais precisa e adaptativa para aplicação das faixas de APP conforme o Código Florestal Brasileiro.

Diante desse cenário, esta ferramenta foi criada com os seguintes objetivos:

- Automatizar o processo de delimitação de APP
- Aumentar a consistência e padronização dos resultados
- Reduzir o tempo de execução em projetos técnicos
- Incorporar a variabilidade da largura do rio ao longo do seu eixo
- Apoiar análises em planejamento urbano, ambiental e territorial

A ferramenta foi pensada para uso direto no QGIS, integrada ao fluxo de trabalho de profissionais que atuam com geoprocessamento aplicado.

**ENGLISH**
This project was developed based on real-world demands in urban and environmental planning projects, particularly for the delineation of Permanent Preservation Areas (APP) along watercourses.

In professional practice, APP delineation is often performed manually or using simplified methods, which can lead to inconsistencies, low reproducibility, and significant processing time, especially in large areas or regions with dense hydrographic networks.

Additionally, river width varies along its course, requiring a more precise and adaptive approach to correctly apply buffer distances according to the Brazilian Forest Code.

In this context, this tool was developed with the following objectives:

- Automate the APP delineation process
- Improve consistency and standardization of results
- Reduce processing time in technical projects
- Incorporate river width variability along its course
- Support urban, environmental, and territorial planning analyses

The tool was designed for direct use within QGIS, integrating seamlessly into GIS-based professional workflows.

---

## Sobre / About

**PORTUGUÊS**
Esta ferramenta calcula a largura do rio a partir de duas margens vetoriais, gera o eixo central e aplica automaticamente a largura de APP correspondente.

**ENGLISH**
This tool calculates river width from two bank lines, generates the centerline, and automatically applies the appropriate riparian buffer.

---

## Funcionalidades / Features

**PORTUGUÊS**

* Cálculo automático da largura do rio
* Geração do eixo central
* Geração de pontos de amostragem de largura
* Aplicação automática das regras do Código Florestal
* Geração de APP contínua (sem falhas entre margens)
* Opção de dissolver todas as APPs
* Opção de remover sobreposição

**ENGLISH**

* Automatic river width calculation
* Centerline generation
* Width sampling points generation
* Automatic application of Brazilian Forest Code rules
* Continuous APP generation (no gaps between banks)
* Option to dissolve all APPs
* Option to remove overlaps

---

## Entrada de dados / Input Data

**PORTUGUÊS**

* Camada de linhas representando as margens do rio
* Cada rio deve possuir exatamente duas linhas (margem esquerda e direita)
* Ambas devem compartilhar o mesmo valor em um campo ID

**ENGLISH**

* Line layer representing river banks
* Each river must have exactly two lines (left and right banks)
* Both must share the same value in an ID field

### Exemplo / Example

| id_arroio | geometria       |
| --------- | --------------- |
| 1         | margem esquerda |
| 1         | margem direita  |

---

## Parâmetros / Parameters

**PORTUGUÊS**

- **Margens do rio**  
  Camada de linhas contendo as duas margens de cada rio.

- **Campo ID**  
  Campo utilizado para identificar cada rio. As duas margens devem possuir o mesmo valor.

- **Distância de amostragem**  
  Intervalo (em metros) utilizado para medir a largura do rio ao longo do seu percurso.  
  Valores menores geram maior precisão, porém aumentam o tempo de processamento.

- **Tolerância para mudança de APP (m)**  
  Define a sensibilidade para alteração da faixa de APP ao longo do rio.  
  Valores maiores evitam mudanças frequentes causadas por pequenas variações de largura.

- **Dissolver todas as APPs**  
  Quando ativado, todas as APPs geradas são unificadas em um único polígono.

- **Remover sobreposição**  
  Remove áreas sobrepostas entre APPs, mantendo apenas a maior faixa conforme a hierarquia de largura.

**ENGLISH**

- **River banks**  
  Line layer containing the two banks of each river.

- **ID field**  
  Field used to identify each river. Both banks must share the same value.

- **Sampling distance**  
  Interval (in meters) used to measure river width along its course.  
  Smaller values increase precision but also processing time.

- **APP change tolerance (m)**  
  Controls sensitivity to changes in buffer width along the river.  
  Higher values reduce frequent changes caused by small width variations.

- **Dissolve all APPs**  
  When enabled, all generated buffers are merged into a single polygon.

- **Remove overlap**  
  Removes overlapping areas between buffers, keeping only the largest one based on width hierarchy.

---

## Saídas / Outputs

**PORTUGUÊS**

* APP: Polígonos de área de preservação permanente
* Pontos de largura: Pontos com largura do rio ao longo do eixo
* Eixo do rio: Linha central gerada

**ENGLISH**

* APP: Permanent preservation area polygons
* Width points: Points containing river width along the centerline
* River centerline: Generated centerline

---

## Metodologia / Methodology

**PORTUGUÊS**

A ferramenta segue um fluxo automatizado para representar de forma mais fiel a variação da largura do rio ao longo do seu percurso:

1. **Amostragem ao longo de uma margem**  
   Pontos são gerados em intervalos regulares ao longo de uma das margens do rio.

2. **Cálculo da largura do rio**  
   Para cada ponto, é calculada a menor distância até a margem oposta, representando a largura local do rio.

3. **Geração do eixo central**  
   O eixo do rio é obtido a partir do ponto médio entre as duas margens ao longo do percurso.

4. **Classificação da APP**  
   A largura do rio é classificada conforme as regras do Código Florestal Brasileiro, definindo a faixa de APP correspondente.

5. **Segmentação ao longo do rio**  
   O rio é dividido em trechos homogêneos conforme a largura e a tolerância definida, evitando variações excessivas na APP.

6. **Geração dos buffers nas margens**  
   Buffers são aplicados individualmente em cada margem para cada trecho.

7. **Construção da geometria contínua da APP**  
   As áreas entre as margens são preenchidas e unificadas com os buffers, garantindo uma APP contínua e sem lacunas, mesmo em rios largos.

**ENGLISH**

The tool follows an automated workflow to accurately represent river width variation along its course:

1. **Sampling along one river bank**  
   Points are generated at regular intervals along one of the river banks.

2. **River width calculation**  
   For each point, the shortest distance to the opposite bank is calculated, representing local river width.

3. **Centerline generation**  
   The river centerline is derived from the midpoint between both banks along the course.

4. **APP classification**  
   River width is classified according to the Brazilian Forest Code, defining the corresponding buffer distance.

5. **Segmentation along the river**  
   The river is divided into homogeneous segments based on width and tolerance, avoiding excessive APP variation.

6. **Buffer generation along river banks**  
   Buffers are applied individually to each bank for each segment.

7. **Continuous APP geometry construction**  
   The space between banks is filled and merged with buffers, ensuring a continuous and gap-free APP, even for wide rivers.

---

## Regras de APP / APP Rules (Brazilian Forest Code)

| Largura do rio / River width | APP   |
| ---------------------------- | ----- |
| até 10 m / up to 10 m        | 30 m  |
| 10–50 m                      | 50 m  |
| 50–200 m                     | 100 m |
| 200–600 m                    | 200 m |
| > 600 m                      | 500 m |

---

## Requisitos / Requirements

**PORTUGUÊS**

* QGIS 3.x ou superior
* Python
* Bibliotecas:
  * numpy
  * shapely (necessário para operações geométricas avançadas)

Observação: a biblioteca `shapely` pode não estar disponível por padrão em algumas instalações do QGIS (especialmente via OSGeo4W), sendo necessária instalação manual.

**ENGLISH**

* QGIS 3.x or higher
* Python
* Libraries:
  * numpy
  * shapely (required for advanced geometric operations)

Note: the `shapely` library may not be available by default in some QGIS installations (especially via OSGeo4W) and may require manual installation.

---

## Como usar / How to Use

**PORTUGUÊS**

1. Abra o QGIS
2. Vá em Processamento > Caixa de Ferramentas

![Abrir Processing Toolbox](images/tutorial_01.png)

3. Na caixa de ferramentas, adicione o script

![Adicionar script](images/tutorial_02.png)
![Adicionar script](images/tutorial_03.png)
![Adicionar script](images/tutorial_04_05.png)

4. Execute a ferramenta "APP Dinâmica"

![Executar ferramenta](images/tutorial_09.png)

5. Configure os parâmetros e execute

![Parâmetros](images/tutorial_07.png)

**ENGLISH**

1. Open QGIS
2. Go to Processing > Toolbox (see steps above)
3. Add the script via the Python Scripts option
4. Run the "APP Dinâmica" tool
5. Set the parameters and run

---

## Limitações / Limitations

**PORTUGUÊS**

* A ferramenta assume que cada rio possui exatamente duas margens
* Linhas muito desalinhadas podem gerar distorções na largura calculada
* Geometrias inválidas podem resultar em falhas na geração da APP
* Em áreas complexas (confluências, ilhas), o resultado pode exigir ajustes manuais

**ENGLISH**

* The tool assumes each river has exactly two bank lines
* Highly misaligned lines may distort width calculation
* Invalid geometries may cause issues in APP generation
* Complex areas (confluences, islands) may require manual adjustments

---

## Autor / Author

Guilherme Silveira Cardoso
Especialista em Geoprocessamento / GIS Specialist

GitHub: https://github.com/gsgeocardoso
LinkedIn: https://www.linkedin.com/in/gscardoso-bio
