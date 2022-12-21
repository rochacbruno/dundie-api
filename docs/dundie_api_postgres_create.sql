CREATE TABLE "public.user" (
	"id" serial NOT NULL,
	"email" varchar(255) NOT NULL UNIQUE,
	"username" varchar(255) NOT NULL UNIQUE,
	"avatar" varchar(255),
	"bio" TEXT,
	"password" TEXT NOT NULL,
	"name" varchar(255) NOT NULL,
	"dept" varchar(255) NOT NULL,
	"currency" varchar(255) NOT NULL,
	CONSTRAINT "user_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.balance" (
	"user_id" bigint NOT NULL UNIQUE,
	"value" DECIMAL NOT NULL DEFAULT '0',
	"updated_at" TIMESTAMP NOT NULL
) WITH (
  OIDS=FALSE
);



CREATE TABLE "public.transaction" (
	"id" serial NOT NULL,
	"user_id" bigint NOT NULL,
	"from_id" bigint NOT NULL,
	"value" DECIMAL NOT NULL,
	"date" TIMESTAMP NOT NULL,
	CONSTRAINT "transaction_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);




ALTER TABLE "balance" ADD CONSTRAINT "balance_fk0" FOREIGN KEY ("user_id") REFERENCES "user"("id");

ALTER TABLE "transaction" ADD CONSTRAINT "transaction_fk0" FOREIGN KEY ("user_id") REFERENCES "user"("id");
ALTER TABLE "transaction" ADD CONSTRAINT "transaction_fk1" FOREIGN KEY ("from_id") REFERENCES "user"("id");




