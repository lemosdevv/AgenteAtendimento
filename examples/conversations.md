# Agent conversation examples

These examples demonstrate the expected behavior of the customer support agent. The assistant responses are illustrative; actual product and order values must come from the SQLite database and the policy document.

## 1. Product search

**Customer:** Quais opções de violões estão disponíveis custando até R$ 1.000?

**Assistant:** Posso consultar as opções disponíveis nessa faixa. Vou apresentar os instrumentos ativos, com estoque e preço atual.

## 2. General store information

**Customer:** Qual é o endereço e o horário de funcionamento da loja?

**Assistant:** A Empório da Música fica na Rua 14 de Maio, 3200, Centro, Campo Grande - MS. O atendimento funciona de segunda a sexta, das 9h às 18h, e aos sábados, das 9h às 13h. Domingos e feriados: fechado.

## 3. Order lookup

**Customer:** Qual é o status do meu pedido #8?

**Assistant:** Vou consultar o status do pedido e, se houver, o código de rastreamento e a previsão de entrega.

## 4. Combined order and policy question

**Customer:** Meu pedido chegou com defeito. Posso trocar?

**Assistant:** A política permite troca por defeito de fabricação em até 30 dias corridos após a compra. É necessário verificar o pedido e confirmar que o problema não foi causado por mau uso, queda, umidade excessiva ou modificação não autorizada.

## 5. Out-of-scope request

**Customer:** Vocês vendem cabos e amplificadores?

**Assistant:** A loja trabalha exclusivamente com instrumentos musicais e não comercializa cabos ou amplificadores. Posso ajudar a encontrar um instrumento do nosso catálogo.

