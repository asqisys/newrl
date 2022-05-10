import requests

NODE_URL = 'http://testnet.newrl.net:8182'
# NODE_URL = 'http://localhost:8182'
WALLET = {"public": "PizgnsfVWBzJxJ6RteOQ1ZyeOdc9n5KT+GrQpKz7IXLQIiVmSlvZ5EHw83GZL7wqZYQiGrHH+lKU7xE5KxmeKg==","private": "zhZpfvpmT3R7mUZa67ui1/G3I9vxRFEBrXNXToVctH0=","address": "0x20513a419d5b11cd510ae518dc04ac1690afbed6"}

# NODE_URL = 'http://testnet.newrl.net:8090'
# WALLET = {"address": "0xc29193dbab0fe018d878e258c93064f01210ec1a","public": "sB8/+o32Q7tRTjB2XcG65QS94XOj9nP+mI7S6RIHuXzKLRlbpnu95Zw0MxJ2VGacF4TY5rdrIB8VNweKzEqGzg==","private": "xXqOItcwz9JnjCt3WmQpOSnpCYLMcxTKOvBZyj9IDIY="}


# NODE_URL = 'http://testnet.newrl.net:8090'
# WALLET = {
#   "public": "pEeY8E9fdKiZ3nJizmagKXjqDSK8Fz6SAqqwctsIhv8KctDfkJlGnSS2LUj/Igk+LwAl91Y5pUHZTTafCosZiw==",
#   "private": "x1Hp0sJzfTumKDqBwPh3+oj/VhNncx1+DLYmcTKHvV0=",
#   "address": "0x6e206561a7018d84b593c5e4788c71861d716880"
# }

def add_wallet(public_key):
  add_wallet_request = {
    "custodian_address": WALLET['address'],
    "ownertype": "1",
    "jurisdiction": "910",
    "kyc_docs": [
  {
    "type": 1,
    "hash": "686f72957d4da564e405923d5ce8311b6567cedca434d252888cb566a5b4c401"
  }
    ],
    "specific_data": {},
    "public_key": public_key
  }

  response = requests.post(NODE_URL + '/add-wallet', json=add_wallet_request)

  unsigned_transaction = response.json()

  response = requests.post(NODE_URL + '/sign-transaction', json={
  "wallet_data": WALLET,
  "transaction_data": unsigned_transaction
  })

  signed_transaction = response.json()

  # print('signed_transaction', signed_transaction)
  print('Sending wallet add transaction to chain')
  response = requests.post(NODE_URL + '/validate-transaction', json=signed_transaction)
  print('Got response from chain\n', response.text)
  assert response.status_code == 200

for public_key in [
    "PizgnsfVWBzJxJ6RteOQ1ZyeOdc9n5KT+GrQpKz7IXLQIiVmSlvZ5EHw83GZL7wqZYQiGrHH+lKU7xE5KxmeKg==",
    "6O5EOxrrDCmL+zemr8UzLKbEW3gY44yTmmaeI3eYfvWUw79FtaLjaMSfSxRr4S78gQlc269CuQ5qKkheJIeCkw==",
    "K7RISj43N9umd+rP/zarVPmUsH/4MQjukYaZeG81nIt8q2RvJaoTOPNVJRmfMHEvpzMWnD4kil7D4zN84cHloA==",
    "QqsMqXqThTfvL7yMXGgI9dRr7mZ4UmF218hSpGP4wA6PokxpKcRu47g9gL4oi7qC3aiIn7q7eGk1ZCXhDP+Ffg==",
    "XEb6F/SwEDdYoB0kISMrFMLOTjjcLfylp46KMcD7pH4Q2HLxBHwgDzzgQRMiBensJcm5uaTzsgnZUqzf/2JO4g==",
    "no9vfbUq5YQP0jCgCRl1h4swT97z7Cw2nxPaGj5KfMqhJVZb9dsToaD4C67M9B9I7HTdiaWDpcxaQOR0a3EbNg==",
    "qcFAa8JxDAubyEjHz2xlkE22GhhPE2HIOxwlna1DfNvtCxPc+D0eK3DHXyvcAuqGgpGhi8baftOkw7He2SqyHw==",
    "ZAvgd5F6QFW+6TD6SI/nc+3DPryAqasXHFdHiMaJVVt8LJ7ga6gHEamLuljTBgRWVkyUVTp311NHXkN+HDLyog==",
    "IMptC9qCne0rgJCNA35PvKts5PPig7Wf1NYk+ffOLU1iulKO3eIILfHVh/syyqDkrrecDfysjfPFcTFKCg2Y5A==",
    "5r7fezzmXi3D4+s8gPnNHfd/KMxnxdjVi73kO/bqrIXnpSI2kVtWYSyxyCu9+mfCXp0TWcGt+G5kG57uRHQdJA==",
    "XHf6TKpVWOqUtUHHOXIe9MiYw5sOIQuSskKawGzCPQWgWKCVxvgc6g6Emcmdl9B5S3B3gpJtSOiFr9G2I+mr/Q==",
    "99dw4RjqGTUamKqE4GGrDxo2GG9IBItkhdEapGyBCv96vJdOxpAwyw+r8kaFvYm2JQ7gtV0vFWV7iixOjXKgFg==",
    "siWxof6FrUAxie0SCRxxLsWCLBBdp8dgWvHc3btV4h0ZpY/8lSHcym5mRhxjyIhk9WRI8sVZvliUZIKsbE5zdQ==",
    "ILjY3nx3faSxWkHDMFp8xc89kmGqr8P+N7VcIL6SoyDBEpquUWLyOuxGLl70NAk47lsUy2MU9/ahWcCnJoQVzw==",
    "wUmapFC2cQGrA88AjQVKnAs0WdD5C221Zpj2R/xjaI2rUaFdGVhLEvl8+6m7r6CjQZONoxjKs02cOmzJE7pUhw==",
    "BZdhXCER0+foqtVOjzfXVi6bE33oS+F7QybRgAKKNG955iIZymjEYZE8RDSKwHI1Ww0iMkaZ6a63ZVR6Q2ZOsw==",
    "ZkhD4hHbzREQfDiRp2W0Glv5L0zIz9lK/RNhluqkGsDONmYT2TkkcdZBUdP5tuxgtcN8W6pjfQjTGaUVmeU8/w==",
    "GbRmnFdJs/Ui/X2QyQqPo9pUwIOfqRxOEc0bDlhikFLgg0eKBMaphuLxBpW860/l+Y26RVEKGhBM3+dhVWBaBA==",
    "hKpfJMvMoOMWvONGJOV9ncQmtupushRNKgYkNLxfnU+1ZnX/XYDZT5ly6oaSypn6fQxtgJFLaHeSSvkZKq0RfA==",
    "qNiSjb6K+5iamYxdp2Qas131gM7o85fdOh9/kCw+iRILvVatxnAbhNbGdddIiC78dYUFzM9EapQ+lu1iRHtt0A==",
    "xd3IMJmgRgl0rBL2TMKBNEQQuz0eQN8UvTLedFOcBJ/KC4JVVWiUE+yn6C5qYP+3p6/77fmZiW0YaSpN2SbHIw==",
    "Ik2mQJ+7aRENe7m3Qngz+Juzuyy0tTazgVxSEb+x3XmzXNaEyxotchZRIm2V1TKDmB4BxhNV9YH9cdrbkyVHxA==",
    "z/GqsOfsjBWSiWqpnanVelBON3nU4QhClkGWMFJ1OqGJO/HDM+rDUS1SelBEgrJF+MjG4S9G+nh5vHN7JrNZCw==",
    "MPSXKGPygraYbOW9apxWQ+dOXVOnKMH1c2rfKKyQHUyli63/k2iGXvCSRR8rX1ktomS0NCm3JB5kuqM0nxKzng==",
    "+1pc+A8bYWfkiOuPv3XMXzJ3xs2TR6lVwHIfkzJfBYiGxKnNhT2IyRxbjlZshlSgmQEhxB+k7PraaBPdN5d7Wg==",
    "o7U2n39SK1NjubeuyWNPDbuc47Ahk9zeHtbI53idE5z8Pc35k0lS5kMq0KDgoi9Kucyke8CS+xzKEi26odpXxA==",
    "JSDoAwJQqmFNVls09fVzcqtAROhh29tLDEXmLqs4ndpCmVdv0kHslX/DhFFq8BFuSv8nfb9uaWfZ9crpFNsDhg==",
    "aPP5K6JPtQXwElTrmPOpOvp2eVizClxYrv4OWwzdtPJv3AFEDF9TMw1hr/Guyaz4x1kwk38fUyIbAs0oyFet9g==",
    "6YCLRYLmn7xLEZoBnvFVAhqMs0RSLHh6qx4+FMFaMhc2vSDh9pxpdLQdjUSPb/JgFsA25Wpkh5r9myC0HbkaOQ==",
    "iRZZT2qgSHpoqMyTsB0xRUUTiXyQlkPYcooj7188dTyO/Rn6lnKJnfQz5KapUBNn2zYebTjFUrlipWvoLWSqww==",
    "PizgnsfVWBzJxJ6RteOQ1ZyeOdc9n5KT+GrQpKz7IXLQIiVmSlvZ5EHw83GZL7wqZYQiGrHH+lKU7xE5KxmeKg=="
]:
  add_wallet(public_key)
